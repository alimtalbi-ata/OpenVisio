"""Vector equipment symbols for the OpenVisio Tk canvas. Author: Abdelhalim Talbi."""
def draw_symbol(canvas, kind, x, y, xy, scale=1.0, selected=False):
    stroke = "#1d4ed8" if selected else "#334155"
    def rect(a,b,c,d,**kw): return canvas.create_rectangle(*xy(x+a,y+b),*xy(x+c,y+d),**kw)
    def oval(a,b,c,d,**kw):
        draw = getattr(canvas, "create_oval", canvas.create_rectangle)
        return draw(*xy(x+a,y+b),*xy(x+c,y+d),**kw)
    def line(a,b,c,d,**kw): return canvas.create_line(*xy(x+a,y+b),*xy(x+c,y+d),**kw)
    common = {"outline":stroke,"width":(2 if selected else 1)*scale}
    if kind in ("server","application"):
        rect(-56,-23,56,20,fill="#dbeafe",**common)
        for yy in (-15,-3,9):
            rect(-47,yy,46,yy+7,fill="#eff6ff",outline="#64748b")
            oval(-40,yy+2,-36,yy+6,fill="#16a34a",outline="")
    elif kind in ("storage","nas"):
        rect(-60,-23,60,22,fill="#dcfce7",**common)
        for yy in (-15,-3,9):
            rect(-50,yy,50,yy+8,fill="#f0fdf4",outline="#64748b")
            for xx in (-40,-20,0,20,40):
                oval(xx-2,yy+2,xx+2,yy+6,fill="#2563eb",outline="")
    elif kind in ("san-switch","network-switch"):
        rect(-62,-15,62,16,fill="#fef3c7" if kind=="san-switch" else "#ede9fe",**common)
        for xx in range(-49,50,14):
            rect(xx,-5,xx+9,5,fill="#1e293b",outline="#64748b")
        line(-50,22,50,22,fill=stroke,width=scale)
    elif kind=="database":
        rect(-42,-15,42,19,fill="#e0e7ff",**common)
        oval(-42,-25,42,-7,fill="#c7d2fe",**common)
        oval(-42,10,42,27,fill="#c7d2fe",**common)
        line(-42,-1,42,-1,fill=stroke,width=scale)
    elif kind=="firewall":
        rect(-48,-24,48,24,fill="#fee2e2",**common)
        for yy in (-11,2,15): line(-46,yy,46,yy,fill="#b91c1c",width=scale)
        for xx in (-22,14): line(xx,-23,xx,-11,fill="#b91c1c",width=scale)
        for xx in (-32,4,32): line(xx,-10,xx,2,fill="#b91c1c",width=scale)
        for xx in (-22,14): line(xx,3,xx,15,fill="#b91c1c",width=scale)
    else:
        rect(-58,-23,58,23,fill="#f1f5f9",**common)
