import pygame as pg
import numpy as np
import pandas as pd
import os

# parametros globales del juego
BG_V = 800 # tamano vertical de la ventana
BG_H = 700 # tamano horizontal de la ventana
IMGS_PATH = 'imgs' # path de imagenes 
VEL_H = 10 # velocidad horizontal del juego 
FREQ_TUBERIAS = 50 # numero de fotogramas para generar una nueva tuberia


# clase Pajaro
class Pajaro:
    FREQ_ACT = 5 # frecuencia de actualizacion de sprites
    GRAVEDAD = 1.5 # gravedad
    VERT_VEL = -15 # velocidad vertical

    def __init__(self, x=100, y=350):
        # elegimos un color aleatoriamente
        ind_color = np.random.randint(1,9)
        
        # sprites del pajaro
        self.sprites = [pg.transform.scale(pg.image.load(f'{IMGS_PATH}/{img}.png'), (3*32, 3*21))
                        for img in [f'bird_{ind_color}1', f'bird_{ind_color}2', f'bird_{ind_color}3', f'bird_{ind_color}2']]

        # coordenadas rectangulares
        self.rect = self.sprites[0].get_rect()

        # actualizamos coordenadas
        self.rect.x = x
        self.rect.y = y

        # indice del sprite inicial
        self.sprint_ind = 0

        # contador de fotogramas
        self.cont = 0

        # velocidad vertical inicial 
        self.v_vel = 0

        # bandera del estado del jugador 
        self.vivo = True

        # puntuacion
        self.puntuacion = 0


    # metodo para el evento de volar
    def volar(self):
        # verificamos que el jugador sigue vivo y no ha salido de pantalla
        if self.vivo and 0 < self.rect.top:
            # incrementamos velocidad vertical
            self.v_vel += self.VERT_VEL


    # metodo para actualizar configuracion
    def actualizar(self):
        # incrementamos conteo de fotogramas
        self.cont += 1

        # verificamos si es necesario actualizar el sprite del jugador
        if self.cont % self.FREQ_ACT==0:
            # incrementamos el indice 
            self.sprint_ind += 1

            # reiniciamos indice de ser necesario
            if self.sprint_ind == 4:
                self.sprint_ind = 0
        
        # actualizamos la dinamica vertical 
        self.v_vel += self.GRAVEDAD 
        self.rect.y += self.v_vel

        # evitamos que el pajaro salga de pantalla al tocar el piso o techo
        self.rect.y = min([self.rect.y, BG_V-20])
        self.rect.y = max([self.rect.y, 0])

        # actualizamos dinamica horizontal si el jugador ha muerto 
        if not self.vivo:
            self.rect.x -= VEL_H

    
    # metodo para dibujar al jugador
    def dibujar(self, pantalla):
        pantalla.blit(self.sprites[self.sprint_ind], self.rect)
    
    
    # deteccion de colisiones
    def detectar_colisiones(self, list_tuberias, puntuacion):
        # colision con el piso
        if BG_V < self.rect.bottom:
            self.vivo = False
            self.puntuacion = puntuacion # actualizamos puntuacion al morir
        
        # verificamos colisiones con tuberias
        for tuberias in list_tuberias:
            if self.rect.colliderect(tuberias.rect1) or self.rect.colliderect(tuberias.rect2):
                self.vivo = False
                self.puntuacion = puntuacion  # actualizamos puntuacion al morir

                # elimininamos velocidad horizontal
                if self.v_vel < 0:
                    self.v_vel = 0
                break

 
# clase para dibujar tuberias
class Tuberias:
    # alturas permitidas para el centro de tuberias
    CENTRO_MIN = 220
    CENTRO_MAX = 580
    GAP = 250 # espacio entre tuberias

    def __init__(self, x=BG_H):
        # definimos las imagenes de las tuberias
        self.img1 = pg.transform.scale2x(pg.image.load(f"{IMGS_PATH}/pipe.png")) # inferior
        self.img2 = pg.transform.flip(self.img1, False, True) # superior

        # coordenadas rectangulares
        self.rect1 = self.img1.get_rect()
        self.rect2 = self.img2.get_rect()

        # posicionamos en coordenada horizontal
        self.rect1.x = x
        self.rect2.x = x

        # elegimos aleatoriamente altura del centro de las coordenadas
        centro = np.random.randint(self.CENTRO_MIN, self.CENTRO_MAX)

        # colocamos tuberias
        self.rect1.top = centro + int(self.GAP/2)
        self.rect2.bottom = centro - int(self.GAP/2)
    

    # metodo para actualizar los objetos
    def actualizar(self):
        self.rect1.x -= VEL_H
        self.rect2.x -= VEL_H
    

    # metodo para dibujar las tuberias
    def dibujar(self, pantalla):
        pantalla.blit(self.img1, self.rect1)
        pantalla.blit(self.img2, self.rect2)



# clase para controlar la escena del juego y sus objetos
class Escena:
    def __init__(self, pantalla, n_jugadores=1, gen=0):
        # texto generacion
        self.gen = gen
        
        # pantalla para dibujar
        self.pantalla = pantalla 

        # contador de fotogramas 
        self.fotogramas = 1
        
        # fondos de pantalla y coordenadas verticales
        self.fondo1 = pg.image.load(f"{IMGS_PATH}/background.png").convert()
        self.rect1 = self.fondo1.get_rect()
        self.fondo2 = pg.image.load(f"{IMGS_PATH}/background.png").convert()
        self.rect2 = self.fondo2.get_rect()

        # ancho de la imagen de fondo
        self.img_h = self.fondo1.get_width()

        # colocamos segundo fondo despues del primero
        self.rect2.x = self.rect1.x + self.img_h

        # creamos los objetos del juego
        self.list_pajaros = [Pajaro(y=ry) for ry in np.random.randint(low=200, high=600, size=n_jugadores)] # poblacion dejugadores
        self.list_tuberias = [Tuberias()] # lista de tuberias 

        # lista de estado en pantalla de jugadores
        self.list_estado_pantalla = [True for pajaro in self.list_pajaros]

        # fuente para puntuacion y generacion
        self.fuente = pg.font.SysFont('consolas', 60)

        # puntuacion de la partida
        self.puntuacion = 0


    # metodo para actualizar configuraciones
    def actualizar(self):
        # desplazamos imagenes de fondo
        self.rect1.x -= VEL_H
        self.rect2.x -= VEL_H

        # verificamos si las imagenes siguen en pantalla
        # de lo contrario colocamos la imagen fuera de pantalla al final de la otra
        if self.rect1.x < -self.img_h:
            self.rect1.x = self.rect2.x + self.img_h
        if self.rect2.x < -self.img_h:
            self.rect2.x = self.rect1.x + self.img_h
        
        # verificamos si se debe agregar una tuberia
        if self.fotogramas % FREQ_TUBERIAS == 0:
            self.list_tuberias.append(Tuberias())

        # conservamos las tuberias que no han salido de pantalla
        self.list_tuberias = [tuberias for tuberias in self.list_tuberias if tuberias.rect1.right>0]

        # actualizamos la puntuacion considerando la frecuencia de tuberias y el estado de los jugadores
        aux_estados = [pajaro.vivo for pajaro in self.list_pajaros if pajaro.vivo]
        if (self.fotogramas-10)%FREQ_TUBERIAS==0 and len(aux_estados)>0 and self.fotogramas>=50:
            self.puntuacion += 1

        # actualizamos el contador de fotogramas
        self.fotogramas += 1

        # verificamos colisiones
        for pajaro, estado in zip(self.list_pajaros, self.list_estado_pantalla):
            if estado:
                pajaro.detectar_colisiones(self.list_tuberias, self.puntuacion)
        
        # actualizamos los objetos del juego
        for pajaro, estado in zip(self.list_pajaros, self.list_estado_pantalla):
            if estado:
                pajaro.actualizar() 
        for tuberias in self.list_tuberias:
            tuberias.actualizar()

        # actualizamos estados de jugadores (evita renderizar perdedores)
        self.list_estado_pantalla = [True if pajaro.rect.x>0 else False for pajaro in self.list_pajaros]


    # metodo para dibujar la escena en la pantalla
    def dibujar(self):
        # dibujamos fondos en pantalla
        self.pantalla.blit(self.fondo1, self.rect1)
        self.pantalla.blit(self.fondo2, self.rect2)

        # dibujamos objetos del juego
        for pajaro, estado in zip(self.list_pajaros, self.list_estado_pantalla):
            if estado:
                pajaro.dibujar(self.pantalla)
        for tuberias in self.list_tuberias:
            tuberias.dibujar(self.pantalla)
        
        # dibujamos puntuacion y generacion
        texto_puntuacion = self.fuente.render(f"{self.puntuacion}", True, (255, 255, 255))
        self.pantalla.blit(texto_puntuacion, (BG_H-100, BG_V-80))
        texto_gen = self.fuente.render(f"GEN: {int(self.gen)}", True, (255, 255, 255))
        self.pantalla.blit(texto_gen, (10, 20))



# generador de poblacion inicial
def generador_poblacion(n_var, n_indv=10, r_inicial = -10.0, r_final=10.0):
    # poblacion con numeros aleatorios en el rango indicado
    poblacion = np.random.uniform(r_inicial, r_final, (n_indv, n_var))
    return poblacion


# operador torneo binario
def torneo_binario(padres, fit_padres):
    ganadores = [] #ganadores del torneo
    fit_ganadores = [] # fitness de los ganadores
    for i in range(len(padres)):
        # se eligen dos invidivuos para participar
        ind_contrincante_1 = np.random.randint(0, len(padres))
        ind_contrincante_2 = np.random.randint(0, len(padres))

        # se consulta su fitness
        fitness_1 = fit_padres[ind_contrincante_1]
        fitness_2 = fit_padres[ind_contrincante_2]
        
        # conservamos al ganador y su fitness
        if fitness_1 < fitness_2:
            ganadores.append(padres[ind_contrincante_1])
            fit_ganadores.append(fitness_1)
        else:
            ganadores.append(padres[ind_contrincante_2])
            fit_ganadores.append(fitness_2)

    return np.array(ganadores), np.array(fit_ganadores)


# operador crossover
def crossover(padres, p_cross=0.9):
    # lista de hijos resultantes
    hijos = []
    
    # iteramos individuos por parejas
    for i in range(0, len(padres), 2):
        # el crossover se realiza con probabilidad p_cross
        if np.random.choice([True, False], p=[p_cross, 1-p_cross]):
            # seleccionamos un valor entre 0 y 1
            alpha = np.random.rand()
            
            # generamos nuevos hijos
            hijo1 = alpha*padres[i] + (1-alpha)*padres[i+1]
            hijo2 = alpha*padres[i+1] + (1-alpha)*padres[i]
            
            # agregamos hijos a la lista
            hijos += [hijo1, hijo2]
        
        # se agregan los padres originales si no se cumple la probabilidad
        else:
            hijos += [padres[i].copy(), padres[i+1].copy()]
    
    return np.array(hijos)


# operador mutacion
def mutacion(hijos, r_inicial, r_final, p_mut=0.2):
    # iteramos sobre los hijos
    for hi in range(len(hijos)):
        # iteramos sobre cada variable del hijo actual
        for vi in range(len(hijos[0])):
            # verificamos si se cumple la probabilidad de mutacion
            if np.random.choice(a=[True, False], p=[p_mut, 1-p_mut]):
                # de ser asi se elige un nuevo valor en el rango especificado
                hijos[hi,vi] = np.random.uniform(r_inicial, r_final)

    return np.array(hijos)


# operador reemplazo generacional
def reemplazo_generacional(padres, hijos, fit_padres, fit_hijos, elitismo=0):
    # en caso de aplicarse elitismo
    if elitismo > 0:
        # ordenamos los padres de mejor a peor
        ind_padres = np.argsort(fit_padres)
        padres = np.array(padres)[ind_padres]
        fit_padres = np.array(fit_padres)[ind_padres]

        # ordenamos los hijos de mejor a peor
        ind_hijos = np.argsort(fit_hijos)
        hijos = np.array(hijos)[ind_hijos]
        fit_hijos = np.array(fit_hijos)[ind_hijos]

        # reemplazamos los peores hijos por los mejores padres
        hijos = np.concatenate([hijos[:-elitismo], padres[:elitismo]])
        fit_hijos = np.concatenate([fit_hijos[:-elitismo], fit_padres[:elitismo]])
        
        return hijos, fit_hijos

    # si no hay elitismo entonces regresamos a la poblacion inicial de hijos
    else: 
        return hijos, fit_hijos
    

# acutalizacion de leaderboard historico
def actualizar_leaderboard(leaderboard, padres, fit_leaderboard, fit_padres):
    # tamano de la poblacion
    n_indv = len(padres)

    # concatenamos genes y fitness
    genes_salida = np.concatenate([leaderboard, padres])
    fit_salida = np.concatenate([fit_leaderboard, fit_padres])

    # eliminamos genes duplicados
    _, ind_unicos = np.unique(genes_salida, axis=0, return_index=True)
    genes_salida = genes_salida[ind_unicos]
    fit_salida = fit_salida[ind_unicos]

    # ordenamos de mejor a peor (historico)
    ind_ord = np.argsort(fit_salida)
    genes_salida = genes_salida[ind_ord]
    fit_salida = fit_salida[ind_ord]

    # conservamos mejores elementos
    return genes_salida[:n_indv], fit_salida[:n_indv]
    

# escritura de resultados
def info_generacion(generacion, poblacion, fit_poblacion):
    # agregamos indice de generacion
    aux_dicc = {'GENERACION': [generacion]*len(poblacion)}

    # agregamos informacion de cada variable
    for i in range(poblacion.shape[1]):
        aux_dicc[f'V{i+1}'] = poblacion[:,i]

    # agregamos fitness de la poblacion
    aux_dicc['FITNESS'] = fit_poblacion

    return pd.DataFrame(aux_dicc)


# UPDATE
def evaluacion_generacion(genes, generacion):
    # pesos de neuronas y tamano de la poblacion UPDATE
    pesos = np.array(genes)
    n_jugadores = len(pesos)

    # definicion de normalizacion con rangos permitidos
    data_min = np.array([0.,-60., -150., -800., -800.])
    data_max= np.array([800., 60., 700., 800., 800.])

    # ejecucion del bucle principal
    # inisializamos modulos
    pg.init()

    # creamos una pantalla
    pantalla = pg.display.set_mode((BG_H, BG_V))

    # creamos un reloj para controlar actualizaciones
    reloj = pg.time.Clock()

    # creacion de escena UPDATE
    escena = Escena(pantalla, n_jugadores=n_jugadores, gen=generacion)

    # creamos variable para mantener el bluque del juego en ejecucion
    aux_val = True

    # bucle principal
    while aux_val and sum(escena.list_estado_pantalla)>0:
        # lista de pajaron vivos y en pantalla
        list_pajaros_vivos = [pajaro for pajaro, estado in zip(escena.list_pajaros, escena.list_estado_pantalla) if estado]

        # obtenemos vectores de informacion
        jugador_ys = [pajaro.rect.y for pajaro in list_pajaros_vivos] # pocision del jugador
        jugador_vys = [pajaro.v_vel for pajaro in list_pajaros_vivos] # velocidad del jugador

        # tuberias mas cercanas
        jugadores_x = max([pajaro.rect.x for pajaro in list_pajaros_vivos]) # pocision de jugadores
        tuberias_delante = [tub for tub in escena.list_tuberias if tub.rect1.x >= jugadores_x-100] # tuberias delante de jugadores

        # nos concentramos en la tuberia mas proxima
        tuberia_objetivo = tuberias_delante[0]
        
        # distancia horizontal a tuberias
        tuberia_distxs = [tuberia_objetivo.rect1.x - jugadores_x]*(len(list_pajaros_vivos))
        
        # distancias verticales a tuberias
        tuberia1_distys = [tuberia_objetivo.rect1.top - jy for jy in jugador_ys]
        tuberia2_distys = [tuberia_objetivo.rect2.bottom - jy for jy in jugador_ys]

        # construimos matriz de informacion
        Xs = np.array([jugador_ys, jugador_vys, tuberia_distxs, tuberia1_distys, tuberia2_distys]).T
        os.system('cls')
        print(pd.DataFrame(Xs, columns=['y', 'v_y', 'd_x', 'd1_y', 'd2_y']))

        # pajaron vivos y sus pesos
        list_pajaros_vivos = [pajaro for pajaro, estado in zip(escena.list_pajaros, escena.list_estado_pantalla) if estado]
        pesos_pajaros_vivos = np.array([gen for gen, estado in zip(pesos, escena.list_estado_pantalla) if estado])

        # definicion de pesos de neuronas
        Ws = np.array(pesos_pajaros_vivos[:,0:-1])
        bs = np.array(pesos_pajaros_vivos[:,-1])

        # normalizamos informacion
        Xs_norm = (Xs-data_min) / (data_max - data_min)

        # evaluacion con neuronas
        act = np.sum(Xs_norm*Ws, axis=1) + bs # producto punto mas bias
        sigm = 1 / (1+np.exp(-act)) # sigmoide

        # activamos vuelo si se supera umbral
        list_vuelos = [True if si > 0.5 else False for si in sigm]

        # mandamos senal de vuelo
        for pajaro, vuelo in zip(list_pajaros_vivos, list_vuelos):
            if vuelo:
                pajaro.volar()

        # iteramos sobre eventos
        for evento in pg.event.get():
            # evento: cerrar ventana
            if evento.type == pg.QUIT: 
                aux_val = False
        
        # actualizamos configuraciones y dibujamos objetos en la escena 
        escena.actualizar()
        escena.dibujar()
        pg.display.flip()

        # limitamos reloj a 30 fotogramas por segundo
        reloj.tick(30)

    # cerramos la aplicacion si se sale del bucle
    pg.quit()

    # vector de puntuacion de jugadores
    return [-1*pajaro.puntuacion for pajaro in escena.list_pajaros]


# semilla aleatoria UPDATE
seed = 1
np.random.seed(seed)

# parametros del algoritmo
n_gen = 35 # numero de generaciones (optimo en generacion 30)
r0 = -4.0 # rangos de valores
rf = 4.0
n_ind = 40 # tamano de poblacion
p_cross = 0.9 # probabilidad crossover
p_mut = 0.20 # probabilidad mutacion
elitismo = 5 # elitismo

# lista de la informacion de cada generacion
list_info = []

# generacion de poblacion inicial
padres = generador_poblacion(n_var=6, n_indv=n_ind, r_inicial=r0, r_final=rf)
fit_padres = evaluacion_generacion(genes=padres, generacion=0)

# agregamos informacion a la lista
list_info.append(info_generacion(generacion=0, poblacion=padres, fit_poblacion=fit_padres))

# definicion de mejores jugadores (historico)
best_genes = np.array(padres).copy()
best_fitness = np.array(fit_padres).copy()

# ejecucion de generaciones
for i in range(n_gen):
    print(f'\nGENERACION: {i+1}')
    # torneo binario
    padres, fit_padres = torneo_binario(padres, fit_padres)

    # crossover
    hijos = crossover(padres, p_cross=p_cross)

    # mutacion
    hijos = mutacion(hijos, r_inicial=r0, r_final=rf, p_mut=p_mut)

    # evaluacion del fitness de los hijos
    fit_hijos = evaluacion_generacion(hijos, generacion=i+1)

    # reemplazo generacional
    hijos, fit_hijos = reemplazo_generacional(best_genes, hijos, best_fitness, fit_hijos, elitismo=elitismo)

    # los hijos se convierten en la proxima generacion de padres
    padres = hijos.copy()
    fit_padres = fit_hijos.copy()

    # actualizacion de leaderboard historico
    best_genes, best_fitness = actualizar_leaderboard(best_genes, padres, best_fitness, fit_padres)

    # agregamos informacion a la lista
    list_info.append(info_generacion(generacion=i+1, poblacion=padres, fit_poblacion=fit_padres))

    
    print(f" - Scores finales: {list_info[-1]['FITNESS'].values}")
    print(f' - Leaderboard: {best_fitness}')
    

# escritura de resultados
final_info = pd.concat(list_info)
final_info.to_csv(f'OUTPUTS/exp_{seed}seed_{n_ind}pob_{rf}r_{p_cross}c_{p_mut}m_{elitismo}e.csv', index=False)