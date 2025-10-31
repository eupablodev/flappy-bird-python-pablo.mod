import pygame
import os
import random

# === Inicialização ===
pygame.init()
pygame.font.init()

# === Constantes ===
TELA_LARGURA = 500
TELA_ALTURA = 800

# Criação da tela normal (com barra de título)
tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
pygame.display.set_caption("Flappy Bird - Pablo")

# === Imagens ===
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join('imgs', 'bg.png')), (TELA_LARGURA, TELA_ALTURA))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

# === Fontes ===
FONTES_PONTOS = pygame.font.SysFont('arial', 50)
FONTES_GAMEOVER = pygame.font.SysFont('arial', 70)
FONTES_REINICIO = pygame.font.SysFont('arial', 30)


# === Classe Passaro ===
class Passaro:
    IMGS = IMAGENS_PASSARO
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 0
        self.tempo = 0
        self.altura = y
        self.angulo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo ** 2) + self.velocidade * self.tempo

        if deslocamento > 16:
            deslocamento = 16
        if deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        self.contagem_imagem += 1
        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 4:
            self.imagem = self.IMGS[1]
        else:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO * 2

        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        centro = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=centro)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


# === Classe Cano ===
class Cano:
    DISTANCIA = 200
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(150, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)
        dist_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        dist_base = (self.x - passaro.x, self.pos_base - round(passaro.y))
        topo_ponto = passaro_mask.overlap(topo_mask, dist_topo)
        base_ponto = passaro_mask.overlap(base_mask, dist_base)
        return topo_ponto or base_ponto


# === Classe Chao ===
class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE
        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


# === Funções de interface ===
def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for cano in canos:
        cano.desenhar(tela)
    for passaro in passaros:
        passaro.desenhar(tela)

    texto = FONTES_PONTOS.render(f"Sua pontuação: {pontos}", True, (255, 255, 255))
    tela.blit(texto, (10, 10))
    chao.desenhar(tela)
    pygame.display.update()


def tela_game_over(tela, pontos):
    tela.fill((0, 0, 0))
    texto1 = FONTES_GAMEOVER.render("GAME OVER", True, (255, 255, 255))
    texto2 = FONTES_REINICIO.render("Pressione R para reiniciar ou ESC para sair", True, (255, 255, 255))
    texto3 = FONTES_PONTOS.render(f"Pontos: {pontos}", True, (255, 255, 255))
    tela.blit(texto1, ((TELA_LARGURA - texto1.get_width()) / 2, 250))
    tela.blit(texto3, ((TELA_LARGURA - texto3.get_width()) / 2, 340))
    tela.blit(texto2, ((TELA_LARGURA - texto2.get_width()) / 2, 430))
    pygame.display.update()


# === Loop Principal ===
def main():
    passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    relogio = pygame.time.Clock()
    pontos = 0
    rodando = True
    game_over = False

    while rodando:
        relogio.tick(30)

        if game_over:
            tela_game_over(tela, pontos)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r:
                        main()
                    elif evento.key == pygame.K_ESCAPE:
                        rodando = False
            continue

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                for passaro in passaros:
                    passaro.pular()

        for passaro in passaros:
            passaro.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    game_over = True
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))
        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            if passaro.y + passaro.imagem.get_height() >= chao.y or passaro.y < 0:
                game_over = True

        chao.mover()
        desenhar_tela(tela, passaros, canos, chao, pontos)

    pygame.quit()
    quit()


if __name__ == '__main__':
    main()
