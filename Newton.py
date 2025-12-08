#Importamos os módulos e os comandos de Python necesarios:
import numpy as np
import sympy as sp
from sympy import Symbol,Derivative,simplify,lambdify
import matplotlib.pyplot as plt
import argparse

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--example", default=None)
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

#Definimos a función cuxas raíces queremos aproximar (cada grupo usará unha función distinta):
#Aquí va el símbolo
z=Symbol('z')

#Metodo de Newton

f=(z**8) - 1
derf=Derivative(f,z,1).doit()
g=simplify(z-f/derf) 

# Número máximo de iteracións para o método elexido:

maxiter=50

#O fractal representarase no rectángulo [a,b]x[c,d]: 

a=-1.5
b=1.5
c=-1.5
d=1.5

        
#Número de puntos usados nos eixos OX e OY para representar o fractal: canto
#maior sexa o número de puntos máis preciso sera o gráfico, pero tamén máis
#tempo se necesitará para levar a cabo os cálculos.

npuntos=300

################### NON MODIFICAR ESTA PARTE DO PROGRAMA #####################
##############################################################################

ff=lambdify(z,f,"numpy")
gg=lambdify(z,g,"numpy")
fractal = np.zeros((npuntos+1,npuntos+1))
tol=1.0e-6

x=np.linspace(a,b,npuntos+1)
y=np.linspace(c,d,npuntos+1)

for i in range(0,npuntos):
    for j in range(0,npuntos):
        z_c = complex(x[i],y[j]) # Usar z_c para el valor de iteración
        n=0
        while (n<maxiter and abs(ff(z_c))>tol):
            try:
                # El cálculo de la siguiente iteración es donde puede fallar
                if abs(gg(z_c))<1/tol:   
                   z_c=gg(z_c)
                   n=n+1
                else:
                   # También se puede manejar como si fuera una no-convergencia
                   break 
            except ZeroDivisionError:
                # Si hay división por cero, detenemos la iteración para este punto
                print("Has intentado dividir por cero en la iteración: ")
                print(n)
                break 
        fractal[npuntos-j,i]=float(n) # El valor n permanece como está al romperse el bucle  

##############################################################################
##############################################################################

print(' ') 
print('MÉTODO DE NEWTON')       
print('A función utilizada é: f(z)=',f)
print('')
print('A súa derivada é: derf(z)=',derf)
print(' ')
print('A función do método de Newton é: g(z)=',g)
print(' ')


#A continuación represéntase a imaxen fractal: recoméndase buscar unha gama de 
#cores atractiva. 
if args.example == "Color Cíclico":
    plt.imshow(fractal,cmap='twilight_shifted', extent=(a, b, c, d))
elif args.example == "Color Secuencial":
    plt.imshow(fractal,cmap='seismic', extent=(a, b, c, d))
elif args.example == "Coolwarm":
    plt.imshow(fractal,cmap='coolwarm', extent=(a, b, c, d))

    plt.colorbar()
    plt.xlabel("x")
    plt.ylabel("y")


plt.savefig('fractal_Newton.png', dpi=2000)
if (args.show is True):
    plt.show()



# Aumentamos DPI para mejor resolución, main.py se encargará de escalar hacia abajo (supersampling)
fig_formulas, ax_formulas = plt.subplots(figsize=(5.5, 3.8), facecolor='white')
ax_formulas.axis('off')
ax_formulas.set_xlim(0, 1)
ax_formulas.set_ylim(0, 1)

# Convertir expresiones sympy a LaTeX
f_latex = sp.latex(f)
derf_latex = sp.latex(derf)
g_latex = sp.latex(g)

# Crear texto con fórmulas
formulas_text = (
    r"$\mathbf{Método\ de\ Newton}$" "\n\n"
    r"$\mathbf{Función:}$" "\n"
    r"$f(z) = " + f_latex + r"$" "\n\n"
    r"$\mathbf{Derivada:}$" "\n"
    r"$f'(z) = " + derf_latex + r"$" "\n\n"
    r"$\mathbf{Iteración:}$" "\n"
    r"$g(z) = " + g_latex + r"$"
)

ax_formulas.text(0.5, 0.5, formulas_text, 
                 ha='center', va='center', 
                 fontsize=14, 
                 transform=ax_formulas.transAxes)

plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
# DPI aumentado a 300 para alta resolución
plt.savefig('formulas_Newton.png', dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor='white')

plt.close(fig_formulas)
plt.close('all') # Asegurar que se cierran todas las figuras y se liberan los archivos

print('Imaxe de fórmulas gardada en: formulas_Newton.png')