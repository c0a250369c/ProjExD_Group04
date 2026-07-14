import pygame as pg
import random #ランダム機能を使うために使用
import os #ファイルやフォルダを操作するためのライブラリ
import sys #Python事態を操作するためのライブラリ
import time

WIDTH = 800 #以下2行色
HEIGHT = 600
GREEN = (34, 139, 34) #以下3行色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Card: #カード1枚を表す
    def __init__(self, rank, suit):
        self.rank = rank #数字部分
        self.suit = suit #マーク部分

    def draw(self, screen, font, x, y): #カードを表示するための関数(画面、文字、横位置、縦位置)
        pg.draw.rect(screen, WHITE, (x, y, 70, 100)) # 白い長方形を描く(x座標、y座標、幅、高さ)
        pg.draw.rect(screen, BLACK, (x, y, 70, 100), 2) # カードの枠線(・・・、太さ)
        text = font.render(f"{self.rank}{self.suit}", True, BLACK) # カードの文字を作る
        screen.blit(text, (x+10, y+35)) # 作った文字を画面に貼り付け (カード左から10、カード上から35)


class Deck: # 山札を管理する(52枚)
    def __init__(self):
        suits = ["H", "D", "C", "S"] # カードのマークを作っている
        ranks = [str(i) for i in range(2, 11)] + ["J", "Q", "K", "A"] # カードの数字を作っている["1","2",・・・,"K","A"]
        self.cards = [] # 空のカード置き場
        for suit in suits: # マークで繰り返し
            for rank in ranks: # 数字で繰り返し
                self.cards.append(Card(rank, suit)) # Cardクラスに入れて対応するカードを作成

        random.shuffle(self.cards) # 山札をランダムに混ぜる


    def draw(self): # 山札からカードを引く処理
        if len(self.cards) == 0: # 山札の枚数を確認
            raise Exception("Deck is empty") # エラーを発生させる/山札が空の場合に文を出力
        return self.cards.pop() # カードを1枚取り出す


class Hand: # 手札を管理する部分
    def __init__(self):
        self.cards = [] # 手札を入れるための空リストを作る

    def add(self, card): # 手札にカードを追加する関数
        self.cards.append(card) # カードをリストの最後に追加

    def total(self): # 手札の合計点を計算する
        value = 0 # 現在の合格点を保存する変数
        aces = 0 # A(エース)の枚数を数える変数
        for card in self.cards: # 手札のカードを順番に調べる
            if card.rank in ["J", "Q", "K"]: # これらの時+10
                value += 10
            elif card.rank == "A": # これらの時　+1 or + 11
                value += 11
                aces += 1
            else:
                value += int(card.rank) # 数字を点数に加える

        while value > 21 and aces: # Aを1点に変更する処理
            value -= 10 # 10点減らす
            aces -= 1 # Aを1枚処理済みにする

        return value # 計算した合計点をかえす


    def draw(self, screen, font, x, y): # 手札を画面に表示する部分
        for i, card in enumerate(self.cards): # 手札のカードを順番に取り出す
            card.draw(screen, font, x+i*90, y) # カードを表示させる、i*90で横にずらす

        total = font.render( f"Player Total : {self.total()}", True, WHITE) # 合計点を文字にする
        screen.blit(total, (x, y+120)) # 合計点をカードの下に表示する


    def draw_dealer(self, screen, font, x, y, hide=True): # ディーラーのカードを表示する関数(ディーラーの手札、ゲーム画面、文字の種類、表示開始位置、表示開始位置、１枚目を隠すかどうか)
        for i, card in enumerate(self.cards): # カードを1枚ずつ取り出す
            if i == 0 and hide: # 条件を確認(1枚目を隠すかどうか判定)
                pg.draw.rect(screen, BLACK, (x+i*90, y, 70, 100)) # 黒い長方形を書く(カードの裏側)
                pg.draw.rect(screen, WHITE, (x+i*90, y, 70,100), 2) # 黒いカードに白い枠線をつける
            else:
                card.draw(screen, font, x+i*90, y) # カードを表示

        if not hide: # カードを隠さない場合(ゲームの終了時)
            total = font.render(f"Dealer Total : {self.total()}", True, WHITE) # ディーラーの合計点を文字にする
            screen.blit(total,(x,y+120)) #合計点をカードの下に表示する


class Message: # ゲーム結果のメッセージを管理するクラス
    def __init__(self):
        self.font = None
        self.text = ""

    def update(self,screen):
        if self.font is None:
            self.font = pg.font.SysFont("msgothic", 30)
        img = self.font.render(self.text, True, WHITE)
        screen.blit(img,(50,520))

class Gmo:# ゲームオーバー画面＆コンティニューボタン
    def __init__(self):
        self.gm = pg.Surface((WIDTH, HEIGHT)) 
        self.fonto = pg.font.SysFont("msgothic", 50)#Game Overのフォントづくり
        self.txt = self.fonto.render("♧ゲームオーバー♦", True, (255, 255, 255))
    def gamen(self, screen):
        pg.draw.rect(self.gm, (0, 0, 0), pg.Rect(0, 0, WIDTH, HEIGHT))
        self.gm.set_alpha(190)
        self.gm.blit(self.txt,[200, 260])
        screen.blit(self.gm, [0, 0])
    # def rebotan(self):

def new_game(): # 新しゲームを作る関数
    deck = Deck() # 山札の作成　(52枚のカードを作る、シャッフルする)
    player = Hand() # プレイヤー用の手札を作る
    dealer = Hand() # ディーラー用の手札を作る
    player.add(deck.draw()) 
    player.add(deck.draw()) # 山札から1枚とり、手札に追加　＝　手札は２枚
    dealer.add(deck.draw()) 
    dealer.add(deck.draw()) # 山札から1枚とり、手札に追加　＝　手札は2枚
    message = Message() # 結果表示用のオブジェクトを作る
    game_over = False # ゲームが終了しているか管理
    if player.total() == 21:# 初期ブラックジャック判定
        if dealer.total() == 21:# ディーラーもブラックジャックの場合
            message.text = "Both Blackjack! Draw!"
        else:
            message.text = "BlackJack! You Win!"

        game_over = True # ゲームを終了する
    return deck, player, dealer, message, game_over # 結果を返す

class Burakkujakku_gamen:

    def burakkujakku_gamen(self, screen: pg.Surface) -> None:
        go_img = pg.Surface((WIDTH, HEIGHT))
        pg.draw.rect(go_img, (0, 0, 0), pg.Rect(0, 0, WIDTH, HEIGHT))
        go_img.set_alpha(180)
        go_img.fill((0, 0, 0))
        
        fonto = pg.font.Font(None, 80)
        txt = fonto.render("Black Jack", True, (255, 255, 255))
        go_img.blit(txt, [WIDTH // 2 -150, HEIGHT // 2 - 40])

        screen.blit(go_img, [0, 0])


def main(): # 実行文
    screen = pg.display.set_mode((WIDTH,HEIGHT)) # 画面を作成
    pg.display.set_caption("Pygame ブラックジャック") # タイトルバーの文字を設定
    font = pg.font.SysFont("msgothic", 25) # 文字用のフォントを作る(フォント、大きさ)
    clock = pg.time.Clock() # ゲームの速度を管理する時計
    gmo = Gmo() #ゲームオーバー画面＆コンティニュー追加機能☆
    is_gameover_screen = False ##ゲームオーバー状態を管理する変数
    deck, player, dealer, message, game_over = new_game() # new_gameを実行(山札、プレイヤー、ディーラー、メッセージ、終了状態)

    if game_over: # 既にゲームが終了しているか確認
        result_timer = pg.time.get_ticks() # 現在の時間を取得
    else:
        result_timer = 0 #タイマーを0にする

    while True:
        
        if game_over and result_timer == 0:
            result_timer = pg.time.get_ticks()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

            if event.type == pg.KEYDOWN and not game_over: # キーボ－ドが押された、ゲーム内である場合に処理
                if event.key == pg.K_h:# HIT、Hキーが押された場合
                    player.add(deck.draw()) # プレイヤーがカードを1枚引く
                    if player.total() > 21: # プレイヤーの合計が21超えたか確認
                        message.text = "Bust! You Lose!"
                        game_over = True # ゲーム終了
                        is_gameover_screen = True ##ゲームオーバー判定用
                        result_timer = pg.time.get_ticks() # 終了した時間を記録、2秒後に新しいゲームを開始
                elif event.key == pg.K_s:# STAND、Sキーが押されえた場合
                    while dealer.total() < 17: # ディーラーのターン
                        dealer.add(deck.draw()) # カードを引く
                    p = player.total() # プレイヤーの点数を保存
                    d = dealer.total() # ディーラーの点数を保存

                    if d > 21: # ディーラーがバーストした場合
                        message.text = "Dealer Bust! You Win!"
                    elif p > d: # プレイヤーの点数が大きい場合
                        message.text = "You Win!"
                    elif p < d: # ディーラーの点数が大きい場合
                        message.text = "You Lose!"
                    else: # 引き分けの場合
                        message.text = "Draw!"

                    game_over = True # ゲーム終了設定
                    result_timer = pg.time.get_ticks() # 終了した時間を記録
            elif event.type == pg.KEYDOWN and is_gameover_screen: # ゲームオーバー条件
                if event.key == pg.K_RSHIFT: # 右Shiftキーが押されたらリスタート
                    deck, player, dealer, message, game_over = new_game()
                    is_gameover_screen = False # ゲームオーバー状態をリセット

        screen.fill(GREEN)
        dealer.draw_dealer(screen, font, 50, 80, not game_over)
        player.draw(screen, font, 50, 320)
        message.update(screen)

        if player.total() == 21 and len(player.cards) == 2:
            bg = Burakkujakku_gamen()
            bg.burakkujakku_gamen(screen)

        pg.display.update()

        if is_gameover_screen: #ここはチップが完成したラ修正する
            gmo.gamen(screen) #画像表示
        elif game_over:# 2秒後に新しいゲーム開始
            if pg.time.get_ticks() - result_timer > 2000:
                deck, player, dealer, message, game_over = new_game()
                result_timer = 0

        pg.display.update() #画面の表示更新
        clock.tick(60) # 1秒間に最大60回処理する,コンピュータによって処理速度が変わる

if __name__ == "__main__":
    pg.init() # pygameを初期化
    main() # ゲーム本体の開始
    pg.quit() # pygameの終了
    sys.exit() # pythonプログラム自体の終了