# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 13:31:30 2021

@author: hbuzzi
"""

import cv2
import sys
import numpy as np

def get_ref_color(image_ref):
    """Função que pega a referência da cor a partir do pixel selecionado usando o mouse
    
    Modo de usar: Avance para o próximo frame apertando espaço, quando encontrar o frame com a cor desejada, pressione a tecla C.
    Ao pressionar a tecla C, mova o mouse e clique sobre a cor desejada, isto fará com que o pixel selecionado seja marcado com um círculo vermelho.
    Se este é o pixel desejado, pressione Enter para confirmar, se clicou errado, pressione Espaço para ignorar a captura atual e poder pressionar C novamente
    
    Caso deseje cancelar, pressione Esc que o código será finalizado
    
    Input: diretório do arquivo de vídeo
    
    Output: Cor de referência desejada no espaço de cor L*a*b"""
    ###Nested Function
    def mouse_event(event, col, lin, flags, *userdata): #Função clique mouse
        if event == cv2.EVENT_LBUTTONDOWN: #Se pressionar o botão esquerdo
            del dsr_point[0]
            dsr_point.append((lin,col))
            copied = image_ref.copy() #Cria uma cópia do frame
            cv2.circle(copied, (col,lin), 1,(0,0,255),-1) #Desenha círculo no ponto clicado
            cv2.imshow(w_name,copied) #Mostra o círculo na imagem copiada (não modifica o frame original), para o usuário saber se está 
            return key
    ###  
    w_name = "Selecione o fundo de referencia" #Nome da janela
    cv2.imshow(w_name, image_ref) #Mostra o frame
    key = 0
    while key != 27 and key != ord('C') and key != ord('c'):
        key = cv2.waitKey(0) #Espera um input do teclado do usuário
    if key == 27: #Se pressionou esc
        cv2.destroyWindow(w_name) #Fecha a janela
        sys.exit() #Termina o código
    elif key == ord('C') or key == ord('c'):
        dsr_point = [(0,0)]
        cv2.setMouseCallback(w_name, mouse_event) # Chama função de clicar mouse
        key = 0
        while key != 13:
            key = cv2.waitKey(0)
        #Se deu Enter, significa que o ponto de referência está certo
        cv2.setMouseCallback(w_name, lambda *args : None) #Termina a função do mouse
        ref = cv2.cvtColor(image_ref, cv2.COLOR_BGR2LAB)[dsr_point[0][0],dsr_point[0][1],:] # Usa a variável global no frame atual para salvar a ref
    cv2.destroyWindow(w_name) #Fecha a janela
    return ref #Retorna a referência

def get_roi(image_intrst):
    """Função que pega a região de interesse (ROI) retangular, com os pontos do retângulo selecionados em ordem horária
    
    Modo de usar: Pressione C para entrar no modo de captura, isso habilitará o uso do mouse.
    Em seguida clique no canto superior esquerdo da região de interesse retangular que deseja selecionar. Um ponto vermelho aparecerá indicando a posição selecionada.
    Caso a posição esteja certa, é possível pressionar Enter, e em seguida, clicar no segundo ponto. Com isto, o ponto vermelho anterior se tornará verde, indicando que foi selecionado.
    Agora, apenas é necessário selecionar os 3 pontos retangulares restantes da região de interesse, em ordem horária.
    
    Caso deseje cancelar, pressione Esc que o código será finalizado
    
    Input: Imagem de interesse
    
    Output: Conjunto de 4 pontos da região de interesse"""
    def mouse_event(event, col, lin, flags, *userdata): #Função clique mouse
        if event == cv2.EVENT_LBUTTONDOWN: #Se pressionar o botão esquerdo
            del dsr_point[i] #Remove a alocação auxiliar
            dsr_point.append((col,lin)) #Adiciona no frame
            copied = image_intrst.copy() #Cria uma cópia do frame
            cv2.circle(copied, (col,lin), 1,(0,0,255),-1) #Desenha círculo no ponto clicado
            cv2.imshow(w_name,copied) #Mostra o círculo na imagem copiada (não modifica o frame original), para o usuário saber se está certo
            return
    ####    
    w_name = "Selecione a regiao de interesse, regiao retangular, em sentido horário" #Nome da janela
    cv2.imshow(w_name, image_intrst) #Mostra o frame
    key = 0
    while key != 27 and key != ord('C') and key != ord('c'):
        key = cv2.waitKey(0) #Espera um input do teclado do usuário
    if key == 27: #Se pressionou esc
        cv2.destroyWindow(w_name) #Fecha a janela
        sys.exit() #Termina o código
    elif key == ord('C') or key == ord('c'):
        dsr_point = [(0,0)] #alocação auxiliar
        i = 0 #iteração dos pontos do retângulo
        cv2.setMouseCallback(w_name, mouse_event) # Chama função de clicar mouse
        for i in range(4): #Percorre 4 pontos do retângulo
            key = 0 #reset da tecla
            while key != 13: #Enquanto não pressionar Enter
                key = cv2.waitKey(0) #Fica esperando e mantém a função do mouse rodando
            #Se deu Enter, significa que o ponto de referência está certo
            cv2.circle(image_intrst, dsr_point[i], 1,(0,255,0),-1) #Desenha na imagem o ponto verde, indicando a confirmação do ponto selecionado
            dsr_point.append((0,0)) #Coloca o ponto auxiliar para o próximo ponto
        cv2.setMouseCallback(w_name, lambda *args : None) #Termina a função do mouse
        del dsr_point[-1] #Remove o último ponto auxiliar
    cv2.destroyWindow(w_name) #Fecha a janela
    return np.array(dsr_point) #Retorna a referência

def frontalPlane_usingROI(image, dsr_p, ref, Limiar):
    """Função que cria o plano frontal de chroma-key apenas sobre a região de interesse de uma imagem
    
    Modo de usar: Ao chamar a função, forneça a imagem que deseja futuramente aplicar o chromaKey, os pontos da região de interesse, a cor de referência do chromaKey, e o Limiar de distância (quanto menor, apenas considera cores mais próximas da cor de referência).
    
    Input: Imagem de interesse, pontos ROI, cor de Ref, Limiar de distância
    
    Output: Imagem da ROI, Plano frontal do chromaKey (chromaKey é excluido, podendo ser somado com o plano de Background para preenchê-lo)"""
    roi = outdoor[dsr_p[:,1].min():dsr_p[:,1].max(),dsr_p[:,0].min():dsr_p[:,0].max()] #Seleciona a ROI da imagem
    D = np.sqrt(np.sum((cv2.cvtColor(roi, cv2.COLOR_BGR2LAB) - ref) ** 2, axis=-1)) #Calcula a imagem de distância
    retval, V0 = cv2.threshold(D,Limiar,255,cv2.THRESH_BINARY) #Pega a imagem de threshold V0
    V0 = np.uint8(V0) #Converte a imagem em uint8
    aux = np.ones((image.shape[0],image.shape[1]),dtype = np.uint8) #Cria a imagem auxiliar do tamanho da imagem
    aux[dsr_p[:,1].min():dsr_p[:,1].max(), dsr_p[:,0].min():dsr_p[:,0].max()] = V0 #Cria a máscara da imagem apenas na regão de interesse
    Frontal = cv2.bitwise_and(image,image,mask=aux) #Aplica a máscara
    return roi, Frontal

def chroma_onROI(Frontal, video, h):
    """Função que junta a imagem de chromakey com o video de background
    
    Modo de usar: Ao chamar a função, forneça a imagem frontal do chromakey, o video de background, e a matriz de homografia.
    O algoritmo aplica a homografia sobre o video, e em seguida adiciona o mesmo ao plano frontal.
    
    Input: Imagem frontal, video background, matriz homografia
    
    Output: Video do chromakey na ROI"""
    height, width, d = Frontal.shape
    while True:
        has_frame, frame = video.read() #Le o frame atual do vídeo
        if not has_frame: #Se não tiver mais frame
            break
        frame_warped = cv2.warpPerspective(frame, h, (width,height)) #Aplica a homografia para fazer o warp do frame
        result = cv2.add(Frontal,frame_warped) #Adiciona o frame modificado em cima do plano frontal da imagem
        cv2.imshow('Resultado',result) #Mostra o resultado
        key = cv2.waitKey(1) #Coleta de tecla
        if key == 27: #Se pressionou esc
            cv2.destroyAllWindows() #Fecha todas as telas
            video.release() #Solta o vídeo chroma
            sys.exit()
    cv2.destroyAllWindows() #Fecha todas as telas
    video.release() #Solta o vídeo chroma

video_name = "output.avi" #Vídeo principal que possui chromakey
video = cv2.VideoCapture(video_name)
outdoor = cv2.imread("outdoor.jpg") #Imagem que será aplicado o vídeo
ref = get_ref_color(outdoor) #Pega a referência da chroma key da imagem
dsr_p = get_roi(outdoor) #Pega os pontos para homografia

## Criação dos pontos de origem da imagem que será transformada, que neste caso, é os frames do vídeo
## Como todo frame possui mesmo tamanho, pode-se apenas criar 1 conjunto de pontos de origem e aplicá-los para todos os frames
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH)) #Largura do vídeo
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)) #Altura do vídeo
orig_p = np.array([(0,0), (width-1, 0), (width-1,height-1), (0,height-1)]) #Cria o vetor de pontos de origem, em ordem horária

h,status = cv2.findHomography(orig_p, dsr_p) #Cria a homografia a partir dos pontos

roi, Frontal = frontalPlane_usingROI(outdoor, dsr_p, ref, 4) #Cria o plano frontal da imagem

chroma_onROI(Frontal, video, h) #Aplica o chroma-key
        
