"""Native SVG equipment glyphs matching OpenVisio canvas semantics."""
def symbol_svg(kind, x, y):
    parts = [f'<g transform="translate({x:g} {y:g})" stroke="#334155" stroke-width="1">']
    def rect(a,b,w,h,fill):
        parts.append(f'<rect x="{a}" y="{b}" width="{w}" height="{h}" fill="{fill}"/>')
    def oval(cx,cy,rx,ry,fill):
        parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}"/>')
    def line(x1,y1,x2,y2,color="#334155"):
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}"/>')
    if kind in ("server", "application"):
        rect(-56,-23,112,43,"#dbeafe")
        for yy in (-15,-3,9):
            rect(-47,yy,93,7,"#eff6ff")
            oval(-38,yy+4,2,2,"#16a34a")
    elif kind in ("storage", "nas"):
        rect(-60,-23,120,45,"#dcfce7")
        for yy in (-15,-3,9):
            rect(-50,yy,100,8,"#f0fdf4")
            for xx in (-40,-20,0,20,40):
                oval(xx,yy+4,2,2,"#2563eb")
    elif kind in ("san-switch", "network-switch"):
        rect(-62,-15,124,31,"#fef3c7" if kind=="san-switch" else "#ede9fe")
        for xx in range(-49,50,14):
            rect(xx,-5,9,10,"#1e293b")
        line(-50,22,50,22)
    elif kind == "database":
        rect(-42,-15,84,34,"#e0e7ff")
        oval(0,-16,42,9,"#c7d2fe")
        oval(0,18.5,42,8.5,"#c7d2fe")
        line(-42,-1,42,-1)
    elif kind == "firewall":
        rect(-48,-24,96,48,"#fee2e2")
        for yy in (-11,2,15):
            line(-46,yy,46,yy,"#b91c1c")
        for xx in (-22,14):
            line(xx,-23,xx,-11,"#b91c1c")
            line(xx,3,xx,15,"#b91c1c")
        for xx in (-32,4,32):
            line(xx,-10,xx,2,"#b91c1c")
    else:
        rect(-58,-23,116,46,"#f1f5f9")
    parts.append("</g>")
    return "".join(parts)
