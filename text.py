from pygame import font
fonts = {}

def draw_shadow(screen, text, pos, font_name, center):
    text_shadow = fonts[font_name].render(text, True, (0, 0, 0))
    if center:
        text_shadow_pos = text_shadow.get_rect(center=(pos[0], pos[1]+3))
    else:
        text_shadow_pos = (pos[0]+3, pos[1]+3)
    screen.blit(text_shadow, text_shadow_pos)

def draw(screen, text, pos, font_family="Arial", font_size=36, color=(255, 255, 255), bold=False, center=False, shadow=False):
    font_name = f'{font_family}_{font_size}{"b" if bold else ""}'
    if  not font_name in fonts:
        fonts[font_name] = font.SysFont(font_family, font_size, bold=bold)
    text_main = fonts[font_name].render(text, True, color)
    if center:
        text_main_pos = text_main.get_rect(center=pos)
    else:
        text_main_pos = pos
    if shadow:
        draw_shadow(screen, text, pos, font_name, center)
    screen.blit(text_main, text_main_pos)
    return fonts[font_name].size(text)[0]
