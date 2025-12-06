import pygame
import sys
import subprocess
import threading
from collections import deque
import os
import textwrap
import os.path

from popups import MethodPopup


pygame.init()
pygame.font.init()

width, height = 1200, 760
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Visualizador de Fractales - by Emefedez")
        
# Colores
BLACK = (0, 0, 0)
GREEN = (120, 255, 95)
RED = (255, 0, 0)
BLUE = (59, 160, 193)
YELLOW = (255, 255, 20)
GREY = (211, 211, 211)
AZULDEBIAN = (0,128,128)
WHITE = (255, 255, 255)

colors = {
    "BLACK": BLACK,
    "GREEN": GREEN,
    "RED": RED,
    "BLUE": BLUE,
    "YELLOW": YELLOW,
    "GREY": GREY,
    "AZULDEBIAN": AZULDEBIAN,
    "WHITE": WHITE,
}

# FUENTE
font = pygame.font.SysFont(None, 40, bold=False)
font_title = pygame.font.SysFont(None, 90, bold=True)
font_btn = pygame.font.SysFont(None, 36, bold=True)
console_font = pygame.font.SysFont("monospace", 16)

# --- LAYOUT ---

# Columna Izquierda (Fórmulas y Consola)
# Fórmulas: Arriba a la izquierda
formulas_rect = pygame.Rect(15, 15, 550, 390)

# Consola: Debajo de las fórmulas
console_rect = pygame.Rect(15, 420, 550, 325)

# Columna Derecha (Fractal y Botones)
# Fractal: Ocupa gran parte de la derecha
fractal_rect = pygame.Rect(580, 15, 605, 450)

# Botones: Debajo del fractal
# Fila 1
button_rectN = pygame.Rect(650, 600, 200, 50)
button_rectH = pygame.Rect(900, 600, 200, 50)
# Fila 2
button_rectC = pygame.Rect(650, 670, 200, 50)
button_rectQ = pygame.Rect(900, 670, 200, 50)

#TITULO
title_surf = font_title.render("AM GRUPO 4.4", True, BLACK)
title_rect = title_surf.get_rect(center=(width // 1.375, 540))
title_bg_rect = title_rect.inflate(0, 2)

# Textos de botones
button_textN = font_btn.render("NEWTON", True, BLACK)
button_textH = font_btn.render("HALLEY", True, BLACK)
button_textC = font_btn.render("CHEBYSHEV", True, BLACK)
button_textQ = font_btn.render("SALIR", True, BLACK)


# --- ESTADO GLOBAL ---
ImagenActual = None
FormulasActual = None

def scale_keep_aspect(image, target_rect):
    """Escala una imagen manteniendo su relación de aspecto para que quepa dentro de target_rect."""
    img_w, img_h = image.get_size()
    target_w, target_h = target_rect.width, target_rect.height

    ratio_img = img_w / img_h
    ratio_target = target_w / target_h

    if ratio_img > ratio_target:
        # La imagen es más ancha que el target (ajustar por ancho)
        new_w = target_w
        new_h = int(new_w / ratio_img)
    else:
        # La imagen es más alta que el target (ajustar por alto)
        new_h = target_h
        new_w = int(new_h * ratio_img)

    return pygame.transform.smoothscale(image, (new_w, new_h))

# Carga inicial si existen archivos por defecto (opcional, por si se reinicia)
def try_load_initial():
    global ImagenActual, FormulasActual
    # Prioridad: Newton > Halley > Chebyshev
    for name in ["Newton", "Halley", "Chebyshev"]:
        f_img = f"fractal_{name}.png"
        form_img = f"formulas_{name}.png"
        if os.path.isfile(f_img):
            try:
                img = pygame.image.load(f_img).convert_alpha()
                ImagenActual = scale_keep_aspect(img, fractal_rect)
            except: pass
        
        if os.path.isfile(form_img):
            try:
                img = pygame.image.load(form_img).convert_alpha()
                FormulasActual = scale_keep_aspect(img, formulas_rect)
            except: pass
        
        if ImagenActual: break

try_load_initial()


# --- CONSOLA ---
console_lines = deque(maxlen=200)
console_lock = threading.Lock()

def append_console(line: str):
    """Añade líneas al buffer de la consola con line-wrapping."""
    with console_lock:
        char_w = max(1, console_font.size("M")[0])
        max_chars = max(10, (console_rect.width - 16) // char_w)
        for sub in line.rstrip("\n").splitlines():
            wrapped = textwrap.wrap(sub, width=max_chars) or [""]
            for w in wrapped:
                console_lines.append(w)

def run_script_capture(script_name: str, example: str = None, show: bool = False):
    """Ejecuta el script y actualiza las imágenes de forma genérica."""
    with console_lock:
        console_lines.clear()

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    cmd = [sys.executable, "-u", script_name]
    if example is not None:
        cmd += ["--example", example]
    if show:
        cmd += ["--show"]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            env=env,
        )
    except Exception as e:
        append_console(f"Error al iniciar {script_name}: {e}")
        return

    def reader():
        global ImagenActual, FormulasActual
        label = f"{script_name} ({example})" if example else script_name
        append_console(f"--- Ejecutando {label} ---")
        
        try:
            while True:
                line = proc.stdout.readline()
                if line == "" and proc.poll() is not None:
                    break
                if line:
                    append_console(line)
        except Exception as e:
            append_console(f"Lectura interrumpida: {e}")
        
        ret = proc.wait()
        append_console(f"--- {label} finalizó (code {ret}) ---")

        if ret == 0:
            # Determinar nombres de archivo basados en el script (ej: Newton.py -> Newton)
            base_name = script_name.replace(".py", "")
            fractal_file = f"fractal_{base_name}.png"
            formulas_file = f"formulas_{base_name}.png"

            # Cargar Fractal
            if os.path.isfile(fractal_file):
                try:
                    # Forzar recarga limpiando caché interna de pygame si existiera (aunque load suele leer de disco)
                    # Una técnica es cargar como bytes primero si hay problemas de bloqueo, pero aquí es simple.
                    img = pygame.image.load(fractal_file).convert_alpha()
                    ImagenActual = scale_keep_aspect(img, fractal_rect)
                    append_console(f"Fractal actualizado: {fractal_file}")
                except Exception as e:
                    append_console(f"Error cargando fractal: {e}")

            # Cargar Fórmulas
            if os.path.isfile(formulas_file):
                try:
                    img = pygame.image.load(formulas_file).convert_alpha()
                    FormulasActual = scale_keep_aspect(img, formulas_rect)
                    append_console(f"Fórmulas actualizadas: {formulas_file}")
                except Exception as e:
                    append_console(f"Error cargando fórmulas: {e}")
            else:
                FormulasActual = None

    threading.Thread(target=reader, daemon=True).start()


if __name__ == "__main__":
    clock = pygame.time.Clock()
    
    # Popups para cada método
    # Aunque Halley y Chebyshev no tengan ejemplos definidos en sus scripts aún,
    # dejamos la estructura lista.
    
    popup_newton = MethodPopup(
        screen=screen, font=font, title="Opciones Newton",
        options=["Ejemplo 1", "Ejemplo 2", "Ejemplo 3"], colors=colors
    )
    
    popup_halley = MethodPopup(
        screen=screen, font=font, title="Opciones Halley",
        options=["Estándar"], colors=colors
    )
    
    popup_chebyshev = MethodPopup(
        screen=screen, font=font, title="Opciones Chebyshev",
        options=["Estándar"], colors=colors
    )

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Manejo de eventos de popups
            if popup_newton.visible:
                popup_newton.handle_event(event)
                continue
            if popup_halley.visible:
                popup_halley.handle_event(event)
                continue
            if popup_chebyshev.visible:
                popup_chebyshev.handle_event(event)
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Botón Newton
                if button_rectN.collidepoint(event.pos):
                    def on_ok_newton(example, show_plot, gui):
                        run_script_capture("Newton.py", example=example, show=show_plot)
                    popup_newton.open(on_ok_newton)
                
                # Botón Halley
                elif button_rectH.collidepoint(event.pos):
                    def on_ok_halley(example, show_plot, gui):
                        # Si el script soportara ejemplos, se pasarían aquí
                        run_script_capture("Halley.py", show=show_plot)
                    popup_halley.open(on_ok_halley)
                
                # Botón Chebyshev
                elif button_rectC.collidepoint(event.pos):
                    def on_ok_chebyshev(example, show_plot, gui):
                        run_script_capture("Chebyshev.py", show=show_plot)
                    popup_chebyshev.open(on_ok_chebyshev)
                
                # Botón Salir
                elif button_rectQ.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        # --- DIBUJADO ---
        screen.fill(AZULDEBIAN)

        # Colores Hover
        mouse_pos = pygame.mouse.get_pos()
        cn = RED if button_rectN.collidepoint(mouse_pos) else BLUE
        ch = RED if button_rectH.collidepoint(mouse_pos) else GREEN
        cc = RED if button_rectC.collidepoint(mouse_pos) else GREY
        cq = RED if button_rectQ.collidepoint(mouse_pos) else YELLOW

        # 1. Fórmulas
        pygame.draw.rect(screen, WHITE, formulas_rect)
        pygame.draw.rect(screen, BLACK, formulas_rect, 2)
        if FormulasActual:
            screen.blit(FormulasActual, formulas_rect)
        else:
            # Texto placeholder si no hay fórmulas
            txt = font.render("Sin fórmulas cargadas", True, GREY)
            screen.blit(txt, txt.get_rect(center=formulas_rect.center))

        # 2. Consola
        pygame.draw.rect(screen, GREY, console_rect)
        pygame.draw.rect(screen, BLACK, console_rect, 2)
        pygame.draw.rect(screen, AZULDEBIAN, title_bg_rect)
        
        with console_lock:
            # Mostrar últimas líneas
            visible_lines = list(console_lines)[-18:] # aprox 18 lineas caben
        
        cy = console_rect.top + 5
        for line in visible_lines:
            surf = console_font.render(line, True, BLACK)
            screen.blit(surf, (console_rect.left + 5, cy))
            cy += console_font.get_linesize()

        # 3. Fractal
        # Dibujar un marco o fondo para el fractal
        pygame.draw.rect(screen, BLACK, fractal_rect, 2)
        if ImagenActual:
            # Centrar la imagen en el rect
            img_rect = ImagenActual.get_rect(center=fractal_rect.center)
            screen.blit(ImagenActual, img_rect)
        else:
            # Placeholder
            pygame.draw.rect(screen, (50, 50, 50), fractal_rect)
            txt = font.render("Fractal no generado", True, WHITE)
            screen.blit(txt, txt.get_rect(center=fractal_rect.center))

        # 4. Botones
        for rect, color, text in [
            (button_rectN, cn, button_textN),
            (button_rectH, ch, button_textH),
            (button_rectC, cc, button_textC),
            (button_rectQ, cq, button_textQ)
        ]:
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
            
            screen.blit(text, text.get_rect(center=rect.center))
            
        
        screen.blit(title_surf, title_rect)

        # 5. Popups (dibujar encima de todo)
        popup_newton.draw()
        popup_halley.draw()
        popup_chebyshev.draw()

        pygame.display.flip()
        clock.tick(120)



