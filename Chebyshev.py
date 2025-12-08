#Importamos os módulos e os comandos de Python necesarios:
import numpy as np
import sympy as sp
from sympy import Symbol, Derivative, simplify, lambdify
import matplotlib.pyplot as plt
import argparse

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--example", default=None)
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

#Definimos a función cuxas raíces queremos aproximar
z = Symbol('z')
f = z/(z**2+z)**(1/2)  # Función por defecto

#Definimos as derivadas da función
derf = Derivative(f, z, 1).doit()
der2f = Derivative(f, z, 2).doit()

#Método de Chebyshev
g = simplify(z - f/derf - (f**2*der2f)/(2*derf**3))

# Parámetros modificables
maxiter = 30
a, b, c, d = -1.1, 0.6, -0.5, 0.5
npuntos = 300

if args.example == "Ejemplo 1":
    f = z/(z**2+z)**(1/2)
    npuntos = 300; a, b, c, d = -1.1, 0.6, -0.5, 0.5
elif args.example == "Ejemplo 2":
    f = z**4 - 1  # Función clásica para fractales
    npuntos = 500; a, b, c, d = -1.5, 1.5, -1.5, 1.5
elif args.example == "Ejemplo 3":
    f = sp.sin(z) + z**2/2  # Función trascendente interesante
    npuntos = 700; a, b, c, d = -3.0, 3.0, -3.0, 3.0

# Resto del código (igual que Newton.py)
ff = lambdify(z, f, "numpy")
gg = lambdify(z, g, "numpy")
fractal = np.zeros((npuntos+1, npuntos+1))
tol = 1.0e-6

x = np.linspace(a, b, npuntos+1)
y = np.linspace(c, d, npuntos+1)

for i in range(0, npuntos):
    for j in range(0, npuntos):
        z_val = complex(x[i], y[j])
        n = 0
        while (n < maxiter and abs(ff(z_val)) > tol):
            if abs(gg(z_val)) < 1/tol:   
               z_val = gg(z_val)
               n = n+1
            else:
               break
        fractal[npuntos-j, i] = float(n)  

print(' ') 
print('MÉTODO DE CHEBYSHEV')       
print('A función utilizada é: f(z)=', f)
print('')
print('A súa primeira derivada é: f\'(z)=', derf)
print('A súa segunda derivada é: f\'\'(z)=', der2f)
print(' ')
print('A función do método de Chebyshev é: g(z)=', g)
print(' ')

plt.imshow(fractal, cmap='plasma', extent=(a, b, c, d))
plt.colorbar()
plt.xlabel("x")
plt.ylabel("y")

plt.savefig('fractal_Chebyshev.png', dpi=2000)
if args.show:
    plt.show()

# Generación de imagen con fórmulas
fig_formulas, ax_formulas = plt.subplots(figsize=(5.5, 3.8), facecolor='white')
ax_formulas.axis('off')
ax_formulas.set_xlim(0, 1)
ax_formulas.set_ylim(0, 1)

f_latex = sp.latex(f)
derf_latex = sp.latex(derf)
der2f_latex = sp.latex(der2f)
g_latex = sp.latex(g)

formulas_text = (
    r"$\mathbf{Método\ de\ Chebyshev}$" "\n\n"
    r"$\mathbf{Función:}$" "\n"
    r"$f(z) = " + f_latex + r"$" "\n\n"
    r"$\mathbf{Primera\ derivada:}$" "\n"
    r"$f'(z) = " + derf_latex + r"$" "\n\n"
    r"$\mathbf{Segunda\ derivada:}$" "\n"
    r"$f''(z) = " + der2f_latex + r"$" "\n\n"
    r"$\mathbf{Iteración:}$" "\n"
    r"$g(z) = " + g_latex + r"$"
)

ax_formulas.text(0.5, 0.5, formulas_text, 
                 ha='center', va='center', 
                 fontsize=14, 
                 transform=ax_formulas.transAxes)

plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
plt.savefig('formulas_Chebyshev.png', dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor='white')

plt.close(fig_formulas)
plt.close('all')
print('Imaxe de fórmulas gardada en: formulas_Chebyshev.png')