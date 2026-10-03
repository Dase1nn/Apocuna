def luminance(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def adjust(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

def contrast_ratio(c1, c2):
    l1 = luminance(c1)
    l2 = luminance(c2)
    bright = max(l1, l2)
    dark = min(l1, l2)
    return (bright + 0.05) / (dark + 0.05)

# Dark Theme (Streamlit default dark + our primary color)
# Title (text on main bg): #FAFAFA on #0E1117
print(f"Dark Theme - Título: {contrast_ratio('#FAFAFA', '#0E1117'):.2f}:1")
# Button (default button uses secondary bg): #FAFAFA on #262730
print(f"Dark Theme - Botón: {contrast_ratio('#FAFAFA', '#262730'):.2f}:1")
# Cards (text on secondary bg): #FAFAFA on #262730
print(f"Dark Theme - Tarjetas: {contrast_ratio('#FAFAFA', '#262730'):.2f}:1")

# Light Theme (Streamlit default light)
# Title: #31333F on #FFFFFF
print(f"Light Theme - Título: {contrast_ratio('#31333F', '#FFFFFF'):.2f}:1")
# Button: #31333F on #F0F2F6
print(f"Light Theme - Botón: {contrast_ratio('#31333F', '#F0F2F6'):.2f}:1")
# Cards: #31333F on #F0F2F6
print(f"Light Theme - Tarjetas: {contrast_ratio('#31333F', '#F0F2F6'):.2f}:1")
