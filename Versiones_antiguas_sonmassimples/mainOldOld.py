import pygame
import sys
import subprocess
import threading
from collections import deque
import os
import textwrap
import os.path


pygame.init()
pygame.font.init()

width, height = 1024, 720
screen = pygame.display.set_mode((width, height))
        
        
# Colores
BLACK = (0, 0, 0)
GREEN = (120, 255, 95)
RED = (255, 0, 0)
BLUE = (59, 160, 193)
YELLOW = (255, 255, 20)
GREY = (211, 211, 211)
AZULDEBIAN = (0,128,128)

# FUENTE
font = pygame.font.SysFont(None, 50, bold=False)
font2 = pygame.font.SysFont(None, 100, bold=True)
console_font = pygame.font.SysFont("monospace", 18)

#Layout de la consola para mostrar los scripts
console_rect = pygame.Rect(15, 320, 550, 340)
plot_rect = pygame.Rect(30, 10, 600, 400)

#Carga de imágenes

Newton = None
Halley = None
Chebyshev = None


if (os.path.isfile("fractal_Newton.png")):
	Newton = pygame.image.load("fractal_Newton.png").convert_alpha()
	NewtonScaled = pygame.transform.smoothscale(Newton, (400, 300))
else: print("No hay fractal por Newton")

if (os.path.isfile("fractal_Halley.png")):
	Halley = pygame.image.load("fractal_Halley.png").convert_alpha()
	HalleyScaled = pygame.transform.smoothscale(Halley, (256, 256))
else: print("No hay fractal por Halley")

if (os.path.isfile("fractal_Chebyshev.png")):
	Chebyshev = pygame.image.load("fractal_Chebyshev.png").convert_alpha()
	ChebyshevScaled = pygame.transform.smoothscale(Chebyshev, (256, 256))
else: print("No hay fractal por Chebyshev")

fractal_rect = pygame.Rect(console_rect.right + 20, 110, width - console_rect.right - 40, 480)

ImagenActual = None






#TITULO
title_surf = font2.render("AM GRUPO 4.4", True, BLACK)
title_rect = title_surf.get_rect(center=(width // 1.45, 80))
title_bg_rect = title_rect.inflate(0, 2)



# Botones de scripts (posiciones separadas para que no se solapen)
button_textN = font.render("NEWTON", True, BLACK)
button_rectN = pygame.Rect(0, 0, 300, 50)
button_rectN.right = width - 60
button_rectN.centery = height // 2 - 35

button_textH = font.render("HALLEY", True, BLACK)
button_rectH = pygame.Rect(0, 0, 300, 50)
button_rectH.right = width - 60
button_rectH.centery = height // 2 + 35

button_textC = font.render("CHEBYSHEV", True, BLACK)
button_rectC = pygame.Rect(0, 0, 300, 50)
button_rectC.right = width - 60
button_rectC.centery = height // 2 + 105

# Botón QUIT 
button_textQ = font.render("QUIT", True, BLACK)
button_rectQ = pygame.Rect(0, 0, 200, 50)
button_rectQ.right = width - 60
button_rectQ.centery = height // 2 + 205

#Ajustes para la consola

console_lines = deque(maxlen=200)
console_lock = threading.Lock()


def append_console(line: str):
    """Añade líneas al buffer de la consola con line-wrapping por anchura del rect."""
    with console_lock:
        # calcular ancho aproximado en caracteres según fuente y rect
        char_w = max(1, console_font.size("M")[0])
        max_chars = max(10, (console_rect.width - 16) // char_w)
        for sub in line.rstrip("\n").splitlines():
            # usar textwrap para hacer wrap por caracteres aproximados
            wrapped = textwrap.wrap(sub, width=max_chars) or [""]
            for w in wrapped:
                console_lines.append(w)


def run_script_capture(name: str):
    """Lanza un script en un proceso hijo sin buffering y captura su salida en tiempo real.
       Borra la consola al iniciar un nuevo script."""
    # limpiar la consola antes de ejecutar
    with console_lock:
        console_lines.clear()

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    try:
        proc = subprocess.Popen(
            [sys.executable, "-u", name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            env=env,
        )
    except Exception as e:
        append_console(f"Error al iniciar {name}: {e}")
        return

    def reader():
        append_console(f"--- Ejecutando {name} ---")
        try:
            # readline para obtener salida incrementalmene
            while True:
                line = proc.stdout.readline()
                if line == "" and proc.poll() is not None:
                    break
                if line:
                    append_console(line)
        except Exception as e:
            append_console(f"Lectura interrumpida: {e}")
        ret = proc.wait()
        append_console(f"--- {name} finalizó (code {ret}) ---")

    threading.Thread(target=reader, daemon=True).start()
    

if __name__ == "__main__":
    
    clock = pygame.time.Clock()
    
    
    # colores iniciales
    while True:
        mouse_pos = pygame.mouse.get_pos()

        # Hover: actualizar colores según posición del ratón
        COLORN = RED if button_rectN.collidepoint(mouse_pos) else BLUE
        COLORH = RED if button_rectH.collidepoint(mouse_pos) else GREEN
        COLORC = RED if button_rectC.collidepoint(mouse_pos) else GREY
        COLORQUIT = RED if button_rectQ.collidepoint(mouse_pos) else YELLOW

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # usar event.pos para detectar clic exacto
                if button_rectN.collidepoint(event.pos):
                    # ejecutar script con el mismo intérprete
                    run_script_capture("Newton.py")
                    if (Newton is not None): ImagenActual = NewtonScaled
                    screen.blit(Newton, (0, 0))
                elif button_rectH.collidepoint(event.pos):
                    run_script_capture("Halley.py")
                    if (Halley is not None): ImagenActual = HalleyScaled
                elif button_rectC.collidepoint(event.pos):
                    run_script_capture("Chebyshev.py")
                    if (Chebyshev is not None): ImagenActual = ChebyshevScaled
                elif button_rectQ.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        # Dibujar fondo
        screen.fill(AZULDEBIAN)
        
        # Consola: fondo claro y borde
        pygame.draw.rect(screen, GREY, console_rect)
        pygame.draw.rect(screen, BLACK, console_rect, 2)
        
        
        with console_lock:
            visible_lines = list(console_lines)[- (console_rect.height // 20) :]

        y = console_rect.top + 8
        for line in visible_lines:
            surf = console_font.render(line, True, BLACK)
            screen.blit(surf, (console_rect.left + 8, y))
            y += console_font.get_linesize()
        
        
		
        # Dibujar botones
        pygame.draw.rect(screen, COLORN, button_rectN)
        screen.blit(button_textN, button_textN.get_rect(center=button_rectN.center))

        pygame.draw.rect(screen, COLORH, button_rectH)
        screen.blit(button_textH, button_textH.get_rect(center=button_rectH.center))

        pygame.draw.rect(screen, COLORC, button_rectC)
        screen.blit(button_textC, button_textC.get_rect(center=button_rectC.center))

        pygame.draw.rect(screen, COLORQUIT, button_rectQ)
        screen.blit(button_textQ, button_textQ.get_rect(center=button_rectQ.center))
        
        pygame.draw.rect(screen, AZULDEBIAN, title_bg_rect)
        screen.blit(title_surf, title_rect)
        
        if (ImagenActual is not None): 
            screen.blit(ImagenActual, plot_rect)
                        
        

        pygame.display.flip()
        clock.tick(60)
        


