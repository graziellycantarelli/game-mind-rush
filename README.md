# 🧠 Mind Rush

## 📖 Sobre o projeto

**Mind Rush** é um jogo educacional no estilo *endless runner*, desenvolvido como projeto interdisciplinar da **Universidade Federal Rural de Pernambuco (UFRPE)**. A proposta é transformar o estudo e a revisão de conteúdos em uma experiência dinâmica e divertida: enquanto o jogador corre e desvia de obstáculos, ele coleta moedas e cérebros que abrem perguntas relacionadas a diferentes cursos da universidade, unindo diversão e aprendizado em uma única jogada.

Cada modo do jogo representa um curso (Computação, Medicina Veterinária, Letras e História, além do modo Flashcards), e responder corretamente às perguntas recupera vidas e aumenta o combo, enquanto errar custa uma vida e torna a partida mais desafiadora. O jogo também conta com um modo de estudo personalizado (estilo flashcards), onde o próprio jogador cadastra suas perguntas e respostas e as revisa durante a corrida, digitando a resposta de cada uma.

## 🎯 Público-alvo

Estudantes em geral e aspirantes a universitários que buscam uma forma mais dinâmica, leve e envolvente de estudar e revisar conteúdos.

## ✅ Funcionalidades atuais

- 🏃 Corrida com pulo, pulo duplo (power-up) e desvio de obstáculos e vilões
- 🧱 Plataformas flutuantes com moedas, perguntas, vilões e obstáculos
- ❓ Perguntas por modo, com 20 segundos para responder e histórico para não repetir questões
- ❤️ Sistema de vidas: acertos recuperam vidas e erros tiram uma
- 🔥 Combo de acertos, pontuação e dificuldade crescente
- ⚡ Power-ups escolhidos a cada sequência de acertos
- 🎴 Modo Flashcard: o jogador cadastra seus cards e responde digitando
- 🗺️ Mapa de modos com um personagem temático para cada curso
- 🛍️ Loja de skins com as moedas coletadas
- 🏆 Ranking pessoal (geral e por modo) e tela de estatísticas
- 🔊 Efeitos sonoros e músicas, com controle de som e música
- ⏸️ Pausa durante a partida e resumo ao final de cada jogo
- 👤 Cadastro, login, troca de senha, troca de nome de usuário e exclusão de conta

## 🛠️ Funcionalidades a incrementar

- 🌟 Conquistas e personagens especiais desbloqueáveis
- 📚 Ampliar o banco de questões de cada curso

## 🎮 Controles

| Ação | Controle |
|---|---|
| Pular / pulo duplo (com o power-up) | `Espaço` ou `↑` |
| Pausar | `Esc`, `P` ou botão na tela |
| Ligar / desligar todo o som | `M` |
| Efeitos e música separadamente | Botões no canto da tela durante a partida |
| Escolher, comprar e navegar | Mouse (a loja e o ranking também aceitam `←` `→` e a roda do mouse) |

## 🚀 Como executar

1. Clone o repositório:
```bash
git clone https://github.com/graziellycantarelli/game-mind-rush.git
cd game-mind-rush
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o jogo:
```bash
python main.py
```

> Testado com Python 3.13 e pygame 2.6.1. O jogo abre em tela cheia, e o som e a música são opcionais: se a pasta `audio` estiver vazia, o jogo roda normalmente, só sem som.

## 📁 Estrutura do projeto

```
game-mind-rush/
├── main.py              # ponto de entrada do jogo
├── audio/               # efeitos (.wav) e músicas (.ogg)
├── fontes/              # fonte pixel do jogo
├── img/                 # fundos, botões, personagens, vilões, obstáculos, skins e logo
└── game/
    ├── motor.py         # laço principal e estados do jogo
    ├── configuracoes.py # tela, fontes e imagens de fundo
    ├── render.py        # desenho do menu, da partida e do game over
    ├── som.py           # efeitos e músicas
    ├── temas.py         # imagens e nomes de cada modo
    ├── catalogo.py      # skins disponíveis na loja
    ├── database/        # contas, pontuações, perguntas, flashcards e loja
    ├── elements/        # personagem, chão e plataformas, vilões, cérebros, moedas, power-ups
    ├── ui/              # telas: conta, loja, ranking, modos, pausa, resumo e outras
    └── util/            # cores, validações e comparação de textos
```

## 🚀 Release 1.0

| Funcionalidade | Descrição |
|---|---|
| Menu / Navegação | Menu principal e navegação entre as funcionalidades do jogo. |
| Cadastro de Jogador | Cadastro de novos jogadores no sistema. |
| Login | Autenticação do jogador para acesso ao sistema. |
| Sistema de Jogo | Execução da partida com movimentação e desvio de obstáculos. |
| Sistema de Pontuação | Pontuação atribuída ao jogador ao esquivar dos obstáculos durante a partida. |

---

## 🚀 Release 2.0

| Funcionalidade | Descrição |
|---|---|
| Troca de Senha | Permite ao jogador atualizar sua senha de acesso. |
| Troca de Nome de Usuário | Permite ao jogador atualizar seu nome de usuário. |
| Banco de Questões | Armazena e disponibiliza questões utilizadas durante o jogo, sem repeti-las até o banco do modo acabar. |
| Apagar Conta | Permite ao jogador excluir sua conta do sistema. |
| Modo Flashcard | O próprio usuário adiciona as perguntas a serem apresentadas durante o jogo e responde digitando; a resposta vale se estiver igual, sem diferenciar maiúsculas e acentos. |
| Power-ups | Adiciona recursos especiais, como escudo e pulo duplo, que beneficiam o jogador durante a partida. |
| Moeda de Pergunta | Permite ao jogador coletar moedas e cérebros durante a partida e responder às perguntas. |
| Mapa de Modos | Seleção do modo em um mapa do campus: o personagem do curso caminha até a ilha escolhida. |
| Loja de Skins | Loja em carrossel, com uma skin grande por vez, para comprar e equipar skins de personagem (com cenário próprio) usando as moedas coletadas. Cada modo tem 2 skins, de 50 e 100 moedas. |
| Ranking Pessoal | Tela com as 5 melhores pontuações do jogador, em carrossel: uma página geral e uma para cada modo de jogo. |
| Plataformas Flutuantes | Plataformas altas, alcançadas com o pulo, que podem trazer moedas, perguntas, vilões ou obstáculos. |
| Obstáculos e Vilões Variados | Cada modo tem 5 obstáculos e 2 vilões, sorteados ao longo da corrida. |
| Sons e Música | Efeitos de pulo, moeda, acerto, erro, power-up e game over, além de músicas para o menu e para a partida, com controle de ligar e desligar. |
| Pausa e Controles na Partida | Pausa por tecla ou botão, com as opções Continuar, Reiniciar e Menu, e botões na tela para ligar e desligar efeitos e música. |
| Resumo da Partida | Ao fim do jogo, mostra pontos, acertos, erros, melhor combo e moedas, destacando quando o jogador bate o próprio recorde. |
