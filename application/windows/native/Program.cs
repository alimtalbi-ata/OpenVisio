// OpenVisio native Windows desktop shell. Author: Abdelhalim Talbi.
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;
using System.Windows.Forms;
using System.IO.Compression;
using System.Reflection;
using System.Security.Cryptography;
using System.Threading;

ApplicationConfiguration.Initialize();
Application.Run(new OpenVisioWindow());

internal sealed class OpenVisioWindow : Form {
 private readonly List<string> recentFiles = new();
 private readonly string recentPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "OpenVisio", "recent.json");
 private readonly string? startupFile = Environment.GetCommandLineArgs().Skip(1).FirstOrDefault();
 private void LoadRecent() {
  try { if (File.Exists(recentPath)) { var paths = System.Text.Json.JsonSerializer.Deserialize<List<string>>(File.ReadAllText(recentPath)) ?? new(); recentFiles.AddRange(paths.Where(File.Exists).Distinct(StringComparer.OrdinalIgnoreCase).Take(8)); } } catch (Exception) { /* corrupted history is non-fatal */ }
  RefreshRecentMenu();
 }
 private void SaveRecent() {
  try { Directory.CreateDirectory(Path.GetDirectoryName(recentPath)!); File.WriteAllText(recentPath, System.Text.Json.JsonSerializer.Serialize(recentFiles)); } catch (Exception) { status.Text = "Historique récent non enregistré"; }
 }
 private ToolStripMenuItem? recentMenu;
 private readonly WebView2 view = new() { Dock = DockStyle.Fill };
 private bool editorReady = false;
 private readonly string diagnosticPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "OpenVisio", "diagnostics.log");
 private void LogDiagnostic(string stage, string detail) {
  try { Directory.CreateDirectory(Path.GetDirectoryName(diagnosticPath)!); File.AppendAllText(diagnosticPath, $"{DateTimeOffset.UtcNow:O} | {stage} | {detail.Replace('\n', ' ')}{Environment.NewLine}"); } catch (Exception) { /* logging must never prevent startup */ }
 }

 private TaskCompletionSource<bool> navigationReady = new(TaskCreationOptions.RunContinuationsAsynchronously);
 private readonly ToolStripStatusLabel status = new("Initialisation…");
 private readonly string contentRoot = PrepareContentRoot();
 private static string PrepareContentRoot() {
  var assembly = Assembly.GetExecutingAssembly();
  using var stream = assembly.GetManifestResourceStream("OpenVisio.Assets.zip");
  if (stream == null) return Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "wwwroot"));
  var cache = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "OpenVisio", "assets", "41.77");
  // Hash the embedded archive, not just the version label: changed or corrupted
  // resources must never be silently accepted from an existing cache.
  using var archiveBytes = new MemoryStream();
  stream.CopyTo(archiveBytes);
  var payload = archiveBytes.ToArray();
  var fingerprint = Convert.ToHexString(SHA256.HashData(payload));
  var marker = Path.Combine(cache, ".complete");
  var index = Path.Combine(cache, "index.html");
  // Validate every extracted file against the embedded archive, not only the marker.
  // This catches edits and corruption occurring after the initial extraction.
  bool CacheValid() {
   try {
    if (!File.Exists(index) || !File.Exists(Path.Combine(cache, "src", "main.js")) ||
        !File.Exists(marker) || File.ReadAllText(marker).Trim() != fingerprint) return false;
    using var expected = new ZipArchive(new MemoryStream(payload), ZipArchiveMode.Read);
    foreach (var entry in expected.Entries) {
     if (string.IsNullOrEmpty(entry.Name)) continue;
     var candidate = Path.GetFullPath(Path.Combine(cache, entry.FullName.Replace('/', Path.DirectorySeparatorChar)));
     if (!candidate.StartsWith(Path.GetFullPath(cache) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase) || !File.Exists(candidate)) return false;
     using var expectedStream = entry.Open();
     using var actualStream = File.OpenRead(candidate);
     if (entry.Length != actualStream.Length) return false;
     var expectedHash = SHA256.HashData(expectedStream);
     var actualHash = SHA256.HashData(actualStream);
     if (!CryptographicOperations.FixedTimeEquals(expectedHash, actualHash)) return false;
    }
    return true;
   }
   catch (IOException) { return false; }
   catch (UnauthorizedAccessException) { return false; }
  }
  // Named mutex serializes cache publication across application instances.
  using var mutex = new Mutex(false, "Local\\OpenVisioAssetsV369");
  bool acquired = false;
  try {
   try { acquired = mutex.WaitOne(TimeSpan.FromSeconds(60)); }
   catch (AbandonedMutexException) { acquired = true; }
   if (!acquired) throw new TimeoutException("Asset cache lock timed out");
   if (CacheValid()) return cache;
   var staging = cache + ".staging-" + Guid.NewGuid().ToString("N");
   Directory.CreateDirectory(staging);
   try {
    using (var archive = new ZipArchive(new MemoryStream(payload), ZipArchiveMode.Read)) {
     foreach (var entry in archive.Entries) {
      var full = Path.GetFullPath(Path.Combine(staging, entry.FullName.Replace('/', Path.DirectorySeparatorChar)));
      if (!full.StartsWith(Path.GetFullPath(staging) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Unsafe asset path");
      if (string.IsNullOrEmpty(entry.Name)) { Directory.CreateDirectory(full); continue; }
      Directory.CreateDirectory(Path.GetDirectoryName(full)!);
      entry.ExtractToFile(full, true);
     }
    }
    if (!File.Exists(Path.Combine(staging, "index.html")) || !File.Exists(Path.Combine(staging, "src", "main.js"))) throw new InvalidDataException("Incomplete embedded assets");
    File.WriteAllText(Path.Combine(staging, ".complete"), fingerprint);
    if (Directory.Exists(cache)) {
     var stale = cache + ".old-" + Guid.NewGuid().ToString("N");
     Directory.Move(cache, stale);
     try { Directory.Move(staging, cache); }
     catch { Directory.Move(stale, cache); throw; }
     // Do not delete old assets: another running WebView2 may still use them.
    } else Directory.Move(staging, cache);
    if (!CacheValid()) throw new InvalidDataException("Asset cache verification failed");
    return cache;
   } finally { if (Directory.Exists(staging)) Directory.Delete(staging, true); }
  } finally { if (acquired) mutex.ReleaseMutex(); }

 }
 public OpenVisioWindow() {
  Text = "OpenVisio 41.77 — Éditeur de diagrammes et SAN";
  Width = 1440; Height = 900; MinimumSize = new System.Drawing.Size(900, 600);
  StartPosition = FormStartPosition.CenterScreen;
  var menu = new MenuStrip();
  var file = new ToolStripMenuItem("Fichier");
  file.DropDownItems.Add("Nouveau", null, (_,_) => NavigateHome());
  file.DropDownItems.Add("Ouvrir un document…  Ctrl+O", null, async (_,_) => await OpenDocumentAsync());
  recentMenu = new ToolStripMenuItem("Documents récents");
  file.DropDownItems.Add(recentMenu);
  file.DropDownItems.Add(new ToolStripSeparator());
  file.DropDownItems.Add("Enregistrer / Exporter…  Ctrl+S", null, (_,_) => Shortcut("s"));
  file.DropDownItems.Add(new ToolStripSeparator());
  file.DropDownItems.Add("Quitter", null, (_,_) => Close());
  var edit = new ToolStripMenuItem("Édition");
  edit.DropDownItems.Add("Annuler", null, (_,_) => Shortcut("z"));
  edit.DropDownItems.Add("Rétablir", null, (_,_) => Shortcut("y"));
  var display = new ToolStripMenuItem("Affichage");
  display.DropDownItems.Add("Actualiser", null, (_,_) => view.Reload());
  display.DropDownItems.Add("Zoom +", null, (_,_) => view.ZoomFactor = Math.Min(3, view.ZoomFactor + .1));
  display.DropDownItems.Add("Zoom -", null, (_,_) => view.ZoomFactor = Math.Max(.5, view.ZoomFactor - .1));
  display.DropDownItems.Add("Zoom 100 %", null, (_,_) => view.ZoomFactor = 1);
  var tools = new ToolStripMenuItem("Outils");
  tools.DropDownItems.Add("Ouvrir le dossier des documents", null, (_,_) => {
   var folder = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
   System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo("explorer.exe", $"\"{folder}\"") { UseShellExecute = true });
  });
  tools.DropDownItems.Add("Dossier des téléchargements", null, (_,_) => {
   var folder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Downloads");
   if (Directory.Exists(folder)) System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo("explorer.exe", $"\"{folder}\"") { UseShellExecute = true });
  });
  var help = new ToolStripMenuItem("Aide");
  help.DropDownItems.Add("Ouvrir les diagnostics", null, (_,_) => {
   var folder = Path.GetDirectoryName(diagnosticPath)!; Directory.CreateDirectory(folder);
   System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo("explorer.exe", $"\"{folder}\"") { UseShellExecute = true });
  });
  help.DropDownItems.Add("À propos", null, (_,_) => MessageBox.Show(this, "OpenVisio 41.77\nAuteur : Abdelhalim Talbi\nApplication Windows .NET + WebView2", "À propos"));
  menu.Items.AddRange(new ToolStripItem[] {file, edit, display, tools, help});
  var strip = new StatusStrip(); strip.Items.Add(status);
  Controls.Add(view); Controls.Add(strip); Controls.Add(menu); MainMenuStrip = menu;
  KeyPreview = true;
  KeyDown += async (_, e) => { if (!e.Control) return; if (e.KeyCode == Keys.O) { e.SuppressKeyPress = true; await OpenDocumentAsync(); } else if (e.KeyCode == Keys.S) { e.SuppressKeyPress = true; Shortcut("s"); } };
  Shown += async (_,_) => { LoadRecent(); await InitializeEditorAsync(); if (!string.IsNullOrWhiteSpace(startupFile) && File.Exists(startupFile)) { if (await WaitForEditorAsync()) await OpenDocumentAsync(startupFile); else status.Text = "Éditeur indisponible : ouverture différée impossible"; } };
  FormClosing += (_,_) => { if (view.CoreWebView2 != null) view.CoreWebView2.Stop(); };
 }
 private async Task InitializeEditorAsync() {
  if (!File.Exists(Path.Combine(contentRoot, "index.html"))) { MessageBox.Show(this, "Ressources OpenVisio manquantes.", "Erreur"); Close(); return; }
  try {
   // A virtual HTTPS host supports JS modules without starting a local HTTP server.
   var userData = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "OpenVisio", "WebView2");
   Directory.CreateDirectory(userData);
   var environment = await CoreWebView2Environment.CreateAsync(userDataFolder: userData);
   await view.EnsureCoreWebView2Async(environment);
   view.CoreWebView2.SetVirtualHostNameToFolderMapping("openvisio.local", contentRoot, CoreWebView2HostResourceAccessKind.DenyCors);
   view.CoreWebView2.ProcessFailed += (_, e) => {
    LogDiagnostic("WebView2.ProcessFailed", e.ProcessFailedKind.ToString());
    status.Text = "Processus WebView2 interrompu — actualisez la vue";
   };
   view.CoreWebView2.Settings.AreDevToolsEnabled = false;
   view.CoreWebView2.Settings.IsStatusBarEnabled = false;
   view.CoreWebView2.Settings.IsZoomControlEnabled = false;
   view.CoreWebView2.DownloadStarting += (_, e) => {
    // The browser proposes the original file name; Windows decides the destination.
    using var dialog = new SaveFileDialog { Title = "Enregistrer l’export OpenVisio", FileName = Path.GetFileName(e.ResultFilePath), Filter = "Tous les fichiers (*.*)|*.*", OverwritePrompt = true, AddExtension = false };
    if (dialog.ShowDialog(this) != DialogResult.OK) { e.Cancel = true; status.Text = "Export annulé"; return; }
    e.ResultFilePath = dialog.FileName;
    status.Text = "Export : " + Path.GetFileName(dialog.FileName);
   };
   view.CoreWebView2.Settings.AreDefaultContextMenusEnabled = true;
   view.CoreWebView2.NavigationCompleted += (_,e) => { editorReady = e.IsSuccess; navigationReady.TrySetResult(e.IsSuccess); status.Text = e.IsSuccess ? "Prêt — édition locale" : $"Erreur de chargement : {e.WebErrorStatus}"; if (!e.IsSuccess) LogDiagnostic("Navigation", e.WebErrorStatus.ToString()); };
   view.CoreWebView2.NewWindowRequested += (_,e) => { e.Handled = true; status.Text = "Ouverture externe bloquée"; };
   view.CoreWebView2.NavigationStarting += (_,e) => { if (!e.Uri.StartsWith("https://openvisio.local/", StringComparison.OrdinalIgnoreCase)) e.Cancel = true; };
   NavigateHome();
  } catch (Exception ex) { LogDiagnostic("Startup", ex.ToString()); MessageBox.Show(this, "WebView2 Runtime est nécessaire.\n" + ex.Message, "OpenVisio"); status.Text = "WebView2 indisponible"; }
 }
 private async Task<bool> WaitForEditorAsync() {
  if (editorReady) return true;
  try { return await navigationReady.Task.WaitAsync(TimeSpan.FromSeconds(20)); }
  catch (TimeoutException) { return false; }
 }
 private async Task OpenDocumentAsync(string? selectedPath = null) {
  if (view.CoreWebView2 == null || !await WaitForEditorAsync()) { status.Text = "Éditeur non prêt"; return; }
  if (selectedPath == null) {
   using var dialog = new OpenFileDialog { Title = "Ouvrir un document OpenVisio", Filter = "Diagrammes OpenVisio (*.json;*.ovjson)|*.json;*.ovjson|Tous les fichiers|*.*", CheckFileExists = true };
   if (dialog.ShowDialog(this) != DialogResult.OK) return;
   selectedPath = dialog.FileName;
  }
  try {
   var info = new FileInfo(selectedPath);
   if (!info.Exists || info.Length > 20 * 1024 * 1024) { MessageBox.Show(this, "Fichier absent ou supérieur à 20 Mo."); return; }
   if (!(string.Equals(info.Extension, ".json", StringComparison.OrdinalIgnoreCase) || string.Equals(info.Extension, ".ovjson", StringComparison.OrdinalIgnoreCase))) { MessageBox.Show(this, "L’ouverture native de documents prend actuellement en charge les fichiers JSON OpenVisio. Les autres imports sont disponibles dans les outils de l’éditeur.", "Format non pris en charge"); return; }
   var data = Convert.ToBase64String(await File.ReadAllBytesAsync(selectedPath));
   var name = System.Text.Json.JsonSerializer.Serialize(info.Name);
   // A standard File object is delivered to the editor's existing file inputs.
   // No arbitrary filesystem path is exposed to page scripts.
   var script = "(() => { const bytes=Uint8Array.from(atob('"+data+"'),c=>c.charCodeAt(0));"+
    "const f=new File([bytes],"+name+");const input=document.getElementById('openJsonInput');"+
    "if(!input)return 'NO_FILE_INPUT';const dt=new DataTransfer();dt.items.add(f);input.files=dt.files;"+
    "input.dispatchEvent(new Event('change',{bubbles:true}));return 'OK';})()";
   var result = await view.ExecuteScriptAsync(script);
   if (result != "\"OK\"") { status.Text = "Import indisponible dans cette vue"; return; }
   recentFiles.RemoveAll(p => string.Equals(p, selectedPath, StringComparison.OrdinalIgnoreCase)); recentFiles.Insert(0, selectedPath);
   if (recentFiles.Count > 8) recentFiles.RemoveRange(8, recentFiles.Count - 8);
   RefreshRecentMenu(); SaveRecent(); status.Text = "Ouvert : " + info.Name;
  } catch (Exception ex) { LogDiagnostic("OpenDocument", ex.ToString()); MessageBox.Show(this, ex.Message, "Impossible d’ouvrir le fichier"); }
 }
 private void RefreshRecentMenu() {
  if (recentMenu == null) return;
  recentMenu.DropDownItems.Clear();
  foreach (var path in recentFiles.Where(File.Exists)) {
   var item = new ToolStripMenuItem(Path.GetFileName(path)) { ToolTipText = path };
   item.Click += async (_,_) => await OpenDocumentAsync(path);
   recentMenu.DropDownItems.Add(item);
  }
  recentMenu.Enabled = recentMenu.DropDownItems.Count > 0;
 }
 private void NavigateHome() { if (view.CoreWebView2 != null) { editorReady = false; navigationReady = new(TaskCreationOptions.RunContinuationsAsynchronously); view.CoreWebView2.Navigate("https://openvisio.local/index.html"); } }
 private void Shortcut(string key) { if (view.CoreWebView2 != null) _ = view.ExecuteScriptAsync($"document.dispatchEvent(new KeyboardEvent('keydown', {{key:'{key}',ctrlKey:true,bubbles:true}}))"); }
}
