import pygame as pg
import random
import os
import sys #Python事態を操作するためのライブラリ

WIDTH = 800 #以下2行色
HEIGHT = 600
GREEN = (34, 139, 34) #以下3行色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Card: #カード1枚を表す
    def __init__(self, rank, suit):
        self.rank = rank #数字部分
        self.suit = suit #マーク部分

    def draw(self, screen, font, x, y):
        pg.draw.rect(screen, WHITE, (x, y, 70, 100))
        pg.draw.rect(screen, BLACK, (x, y, 70, 100), 2)

        text = font.render(f"{self.rank}{self.suit}", True, BLACK)
        screen.blit(text, (x+10, y+35))


class Deck:

    def __init__(self):

        suits = ["H", "D", "C", "S"]
        ranks = [str(i) for i in range(2, 11)] + ["J", "Q", "K", "A"]
        self.cards = []
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(rank, suit))

        random.shuffle(self.cards)


    def draw(self):

        # 山札切れ防止
        if len(self.cards) == 0:
            raise Exception("Deck is empty")
        return self.cards.pop()


class Hand:

    def __init__(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    def total(self):
        value = 0
        aces = 0
        for card in self.cards:
            if card.rank in ["J", "Q", "K"]:
                value += 10
            elif card.rank == "A":
                value += 11
                aces += 1
            else:
                value += int(card.rank)

        while value > 21 and aces:
            value -= 10
            aces -= 1

        return value


    def draw(self, screen, font, x, y):
        for i, card in enumerate(self.cards):
            card.draw(screen, font, x+i*90, y)

        total = font.render( f"Player Total : {self.total()}", True, WHITE)
        screen.blit(total, (x, y+120))


    def draw_dealer(self, screen, font, x, y, hide=True):
        for i, card in enumerate(self.cards):
            if i == 0 and hide:
                pg.draw.rect(screen, BLACK, (x+i*90, y, 70, 100))
                pg.draw.rect(screen, WHITE, (x+i*90, y, 70,100), 2)
            else:
                card.draw(screen, font, x+i*90, y)

        if not hide:
            total = font.render(f"Dealer Total : {self.total()}", True, WHITE)
            screen.blit(total,(x,y+120))

class Chips:
    def __init__(self):
        self.total_chips = 1000  # 初期所持金
        self.current_bet = 10    # デフォルトの賭け金
        self.min_bet = 10        # 最低賭け金

    def adjust_bet(self, amount):
        """ 十字キーでベット額を増減。所持チップを越えないように制御 """
        self.current_bet += amount
        if self.current_bet < self.min_bet:
            self.current_bet = self.min_bet
        if self.current_bet > self.total_chips:
            self.current_bet = self.total_chips

    def place_bet(self):
        """ ベット確定時に所持金から引く """
        self.total_chips -= self.current_bet

    def settle_payout(self, outcome):
        """ 勝敗に応じて配当金を計算し、所持金に加算する """
        # outcomeの種類: "win", "blackjack", "draw", "lose"
        if outcome == "blackjack":
            # ブラックジャックは2.5倍払い戻し（1.5倍の利益）
            payout = int(self.current_bet * 2.5)
        elif outcome == "win":
            # 通常勝利は2倍払い戻し
            payout = self.current_bet * 2
        elif outcome == "draw":
            # 引き分けはベット額の払い戻し
            payout = self.current_bet
        else:
            # 負けは0
            payout = 0
            
        self.total_chips += payout
        return payout

    def draw_ui(self, screen, font):
        """ 画面右上に現在の所持金と現在のベット額を常時表示 """
        chips_text = font.render(f"Total Chips: {self.total_chips}", True, GOLD)
        bet_text = font.render(f"Current Bet: {self.current_bet}", True, GOLD)
        screen.blit(chips_text, (WIDTH - 250, 20))
        screen.blit(bet_text, (WIDTH - 250, 50))

class Message:
    def __init__(self, font):
        self.font = pg.font.SysFont("msgothic", 30)
        self.text = ""

    def update(self,screen):
        img = self.font.render(self.text, True, WHITE)
        screen.blit(img,(50,520))



def new_game(msg_font, chips):
    deck = Deck()
    player = Hand()
    dealer = Hand()
    player.add(deck.draw())
    player.add(deck.draw())
    dealer.add(deck.draw())
    dealer.add(deck.draw())
    message = Message(msg_font)
    game_over = False
    outcome = None  # 配当計算用の勝敗ステータス

    # 破産チェック：次のゲーム開始時にチップが0なら1000に戻す
    if chips.total_chips <= 0:
        chips.total_chips = 1000
        chips.current_bet = 10

    # ベット額が所持金を上回っていたら自動調整
    if chips.current_bet > chips.total_chips:
        chips.current_bet = chips.total_chips

    return deck, player, dealer, message, game_over, outcome

    if player.total() == 21:# 初期ブラックジャック判定
        if dealer.total() == 21:# ディーラーもブラックジャックの場合
            message.text = "Both Blackjack! Draw!"
        else:
            message.text = "BlackJack! You Win!"

        game_over = True
    


def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Pygame ブラックジャック")
    
    # フォントは内蔵のデフォルト(None)を使用
    font = pg.font.Font(None, 30)
    msg_font = pg.font.Font(None, 40)
    clock = pg.time.Clock()
    
    chips = Chips()
    deck, player, dealer, message, game_over, outcome = new_game(msg_font, chips)

    betting_phase = True
    result_timer = 0

    while True:
        # --- 1. イベント処理 ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

            if event.type == pg.KEYDOWN:
                if betting_phase:
                    if event.key == pg.K_UP:
                        chips.adjust_bet(10)
                    elif event.key == pg.K_DOWN:
                        chips.adjust_bet(-10)
                    elif event.key == pg.K_RIGHT:
                        chips.adjust_bet(100)
                    elif event.key == pg.K_LEFT:
                        chips.adjust_bet(-100)
                    elif event.key == pg.K_RETURN:
                        chips.place_bet()
                        betting_phase = False
                        
                        if player.total() == 21:
                            game_over = True
                            if dealer.total() == 21:
                                message.text = "Both Blackjack! Draw!"
                                outcome = "draw"
                            else:
                                message.text = "BlackJack! You Win!"
                                outcome = "blackjack"

                        if game_over:
                            payout = chips.settle_payout(outcome)
                            message.text += f" (+{payout} chips)"
                            result_timer = pg.time.get_ticks()
                
                elif not game_over:
                    if event.key == pg.K_h:
                        player.add(deck.draw())
                        if player.total() > 21:
                            message.text = "Bust! You Lose!"
                            outcome = "lose"
                            game_over = True
                            payout = chips.settle_payout(outcome)
                            result_timer = pg.time.get_ticks()

                    elif event.key == pg.K_s:
                        while dealer.total() < 17:
                            dealer.add(deck.draw())
                        p = player.total()
                        d = dealer.total()

                        if d > 21:
                            message.text = "Dealer Bust! You Win!"
                            outcome = "win"
                        elif p > d:
                            message.text = "You Win!"
                            outcome = "win"
                        elif p < d:
                            message.text = "You Lose!"
                            outcome = "lose"
                        else:
                            message.text = "Draw!"
                            outcome = "draw"

                        game_over = True
                        payout = chips.settle_payout(outcome)
                        message.text += f" (+{payout} chips)"
                        result_timer = pg.time.get_ticks()

        # --- 2. 画面のクリア (毎フレーム必ず最初に1回だけ行う) ---
        screen.fill(GREEN)
        
        # --- 3. 要素の描画 (上から順番に重ねて描く) ---
        chips.draw_ui(screen, font)

        if betting_phase:
            # ベット選択画面のテキスト表示
            guide_text1 = msg_font.render("Select Your Bet Amount", True, WHITE)
            guide_text2 = font.render("Press UP / DOWN to Change. Enter to Start.", True, WHITE)
            screen.blit(guide_text1, (50, 250))
            screen.blit(guide_text2, (50, 300))
        else:
            # 試合画面の表示
            dealer.draw_dealer(screen, font, 50, 80, not game_over)
            player.draw(screen, font, 50, 320)
            message.update(screen)
            
            if not game_over:
                guide = font.render("[H]: Hit  [S]: Stand", True, WHITE)
                screen.blit(guide, (50, 20))

        # --- 4. 画面の更新 (描画がすべて終わった後に1回だけ呼ぶ) ---
        pg.display.update()

        # --- 5. 時間経過によるゲームの進行リセット ---
        if game_over and not betting_phase:
            if pg.time.get_ticks() - result_timer > 2500:
                deck, player, dealer, message, game_over, outcome = new_game(msg_font, chips)
                betting_phase = True

        # フレームレートを60に固定
        clock.tick(60)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()