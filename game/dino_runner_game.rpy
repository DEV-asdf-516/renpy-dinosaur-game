# Dinosaur Game

# 공룡
image dino_run1 = "images/dino/dino_run1.png"
image dino_run2 = "images/dino/dino_run2.png"
image dino_down1 = "images/dino/dino_down1.png"
image dino_down2 = "images/dino/dino_down2.png"
image dino_jump = "images/dino/dino_jump.png"
image dino_hit = "images/dino/dino_dead.png"

# 배경 
image bg = "images/other/background.png"
image track = "images/other/track.png"
image cloud = "images/other/cloud.png"

# 장애물 
image large_cactus1 = "images/cactus/large_cactus1.png"
image large_cactus2 = "images/cactus/large_cactus2.png"
image large_cactus3 = "images/cactus/large_cactus3.png"

image small_cactus1 = "images/cactus/small_cactus1.png"
image small_cactus2 = "images/cactus/small_cactus2.png"
image small_cactus3 = "images/cactus/small_cactus3.png"

image bird1 = "images/bird/bird1.png"
image bird2 = "images/bird/bird2.png"

define SCREEN_WIDTH = 1800
define score = 0

init python:
    import random, pygame, time

    # 공룡
    class Dino: 
        X_POS = 200 # 초기 X 위치
        Y_POS = 600 # 초기 Y 위치
        Y_POS_DOWN = 630  # DOWN시 Y위치
        JUMP_VEL = 10 # 가속도

        def __init__(self):
            self.run_imgs = [Transform("dino_run1"), Transform("dino_run2")] # 달리기
            self.down_imgs = [Transform("dino_down1"), Transform("dino_down2")] # 눕기
            self.jump_img = Transform("dino_jump")
            self.dead_img = Transform("dino_hit")
            self.is_jump = False 
            self.is_down = False 
            self.is_run = True
            self.step_idx = 0 
            self.img = self.run_imgs[0]
            self.jump_velocity = self.JUMP_VEL
            self.x = self.X_POS 
            self.y = self.Y_POS
            self.animation_timer = 0

        def update(self,game_speed,dt): # 움직임 갱신
            if self.is_run: 
                self.run(dt)
            if self.is_jump:
                self.jump(game_speed,dt)
            if self.is_down:
                self.down(dt)

        def animate(self,imgs,dt):
            self.animation_timer += dt
            if self.animation_timer > 0.1:
                self.step_idx = (self.step_idx + 1) % len(imgs)
                self.img = imgs[self.step_idx]
                self.animation_timer = 0

        def run(self,dt):
            self.animate(self.run_imgs,dt)
            self.x = self.X_POS 
            self.y = self.Y_POS 
                      
        def down(self,dt):
            self.animate(self.down_imgs,dt)
            self.x = self.X_POS
            self.y = self.Y_POS_DOWN

        def jump(self,game_speed,dt):
            self.img = self.jump_img
            if self.is_jump:
                self.y -= self.jump_velocity * 3.6
                self.jump_velocity -= 0.05 * (game_speed * dt)
            if self.jump_velocity < - self.JUMP_VEL: 
                self.is_jump = False # 점프 종료 
                self.is_run = True # 다시 달리기
                self.jump_velocity = self.JUMP_VEL # 가속도 초기화
                self.y = self.Y_POS # y위치 
        
        def dead(self,x,y): 
            self.img = self.dead_img
            self.x = x 
            self.y = y

    # 장애물
    class Obstacle:
        def __init__(self,img,y_pos):
            self.img = img 
            self.x = SCREEN_WIDTH
            self.y = y_pos 
        
        def update(self,game_speed,dt):
            self.x -= game_speed * dt # 게임 속도만큼 x좌표 감소
        
        def is_out_screen(self): # 장애물이 화면밖으로 나갔는지 검사
            return self.x < - SCREEN_WIDTH
    
    class SmallCactus(Obstacle): # 작은 선인장 
        def __init__(self):
            self.y = 620
            self.img = Transform("small_cactus" + str(random.randint(1,3))) # 랜덤으로 작은 선인장 이미지 선택
            super().__init__(self.img,self.y)
    
    class LargeCactus(Obstacle): # 큰 선인장
        def __init__(self):
            self.y = 600
            self.img = Transform("large_cactus" + str(random.randint(1,3)))
            super().__init__(self.img,self.y)

    class Bird(Obstacle): # 새 
        BIRD_Y = [540,560,610]
        def __init__(self):
            self.bird_imgs = [Transform("bird1"),Transform("bird2")]
            self.img = self.bird_imgs[random.randint(0,1)]
            self.y = random.choice(self.BIRD_Y)
            self.animation_timer = 0
            self.idx = 0
            super().__init__(self.img,self.y)
        
        def fly(self,game_speed,dt): # 날갯짓
            super().update(game_speed,dt)
            self.animation_timer += dt
            if self.animation_timer > 0.1: # 0.1초마다 이미지 변경
                self.idx = (self.idx + 1) % len(self.bird_imgs)
                self.img = self.bird_imgs[self.idx]
                self.animation_timer = 0 
        
    class Cloud: # 구름
        def __init__(self):
            self.x = SCREEN_WIDTH - random.randint(800,1000)
            self.y = random.randint(50,100)
            self.img = Transform("cloud")
        
        def update(self,width,game_speed,dt): # 구름 움직임
            self.x -= game_speed * dt
            if self.x < - width:
                self.x = SCREEN_WIDTH + random.randint(800,1000)
                self.y = random.randint(50,100)


    class DinosaurGame(renpy.Displayable): # 게임
        def __init__(self):
            renpy.Displayable.__init__(self) # renpy의 Displayable을 상속받아 구현
            self.game_speed = 1000
            self.obstacles = []
            self.score = 0 
            self.bg_x = 0 
            self.bg_y = 680
            self.bg_img = Transform("track")
            self.game_over = False 
            self.dino = Dino()
            self.cloud = Cloud()
            self.oldst = None
            self.paused = False 
            self.game_over_delay = None

        def move_track(self,dt): # 배경 움직임
            if self.bg_x <= - SCREEN_WIDTH:
                self.bg_x = 0
            self.bg_x -= self.game_speed * dt

        def create_obstacle(self): # 랜덤 장애물 생성
            if len(self.obstacles) < 3: 
                if not self.obstacles or (self.obstacles and self.obstacles[-1].x < 200):
                    obs_type = random.randint(0,2)
                    if obs_type == 0: # 작은 선인장
                        self.obstacles.append(SmallCactus())
                    if obs_type == 1: # 큰 선인장
                        self.obstacles.append(LargeCactus())
                    if obs_type == 2: # 새
                        self.obstacles.append(Bird())

        def update_obstacle(self,dt): # 장애물 갱신
            for obstacle in self.obstacles:
                if isinstance(obstacle,Bird):
                    obstacle.fly(self.game_speed,dt) # 날갯짓
                else:
                    obstacle.update(self.game_speed,dt) # 장애물 업데이트
                if obstacle.is_out_screen():
                    self.obstacles.remove(obstacle)  # 화면 밖으로 나간 장애물 제거

        def check_collision(self,dino_render,obs_render,obs): # 충돌 체크
            dino_width, dino_height = dino_render.get_size()  # 공룡 크기
            obs_width, obs_height = obs_render.get_size() # 장애물 크기
            dino_rect = pygame.Rect(self.dino.x, self.dino.y, dino_width, dino_height) # 사각형 생성  
            obs_rect = pygame.Rect(obs.x, obs.y,obs_width,obs_height) 
            if dino_rect.colliderect(obs_rect): # 장애물과 공룡이 충돌했는지 확인
                return True 
            return False 

        def visit(self): # 사용하는 image 반환
            return [self.dino.img,self.bg_img, self.cloud.img] + [obs.img for obs in self.obstacles]

        def render(self,width,height,st,at): # 화면에 그림
            render = renpy.Render(width,height)

            if self.oldst is None:
                self.oldst = st 
            
            dtime = st - self.oldst 
            self.oldst = st

            if not self.paused and not self.game_over:
                # 점수 누적
                self.score += 1
                if self.score % 100 == 0:
                    self.game_speed += 10 # 게임 속도 증가
                
                self.update_obstacle(dtime) # 장애물 이동
                self.dino.update(self.game_speed,dtime) # 공룡 이동
                self.move_track(dtime) # 배경 이동
                self.cloud.update(width,self.game_speed,dtime) # 구름 이동

            # 공룡 
            dino_render = renpy.render(self.dino.img,width,height,st,at)
            render.blit(dino_render,(self.dino.x,self.dino.y))

            # 장애물 
            self.create_obstacle()
            for obstacle in self.obstacles:
                obs_render = renpy.render(obstacle.img,width,height,st,at)
                render.blit(obs_render,(obstacle.x,obstacle.y))
                if not self.paused and not self.game_over:
                    if self.check_collision(dino_render,obs_render,obstacle): # 충돌체크
                        self.dino.dead(self.dino.x,self.dino.y)
                        global score
                        self.game_over = True 
                        self.game_over_delay = None
                        score = self.score
                        break

            # 배경
            bg_render = renpy.render(self.bg_img,width,height,st,at)
            render.blit(bg_render,(self.bg_x,self.bg_y))
            render.blit(bg_render,(self.bg_x + width,self.bg_y)) # 배경이 매끄럽게 이어지도록

            # 구름
            cloud_render = renpy.render(self.cloud.img,width,height,st,at)
            render.blit(cloud_render,(self.cloud.x,self.cloud.y))

            # 점수
            score_text = Text(f"SCORE: {self.score}", color = "#FAFAFA") 
            score_render = renpy.render(score_text,width,height,st,at) 
            render.blit(score_render, ((width//1.15),40))

            renpy.redraw(self,0)

            if self.game_over:
                if self.game_over_delay is None:
                    self.game_over_delay = time.time()
                elif time.time() - self.game_over_delay > 0.3:
                    renpy.jump("game_over")

            return render 

        def event(self,event,x,y,st): # 키 입력 처리
            if not self.paused:
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_UP or event.key == pygame.K_SPACE) and not self.dino.is_jump:
                        # 윗 방향키나 스페이스바 누르면 점프
                        self.dino.is_down = False 
                        self.dino.is_run = False 
                        self.dino.is_jump = True
                    elif event.key == pygame.K_DOWN and not self.dino.is_jump:
                        # 아래 방향키 누르면 고개숙임
                        self.dino.is_down = True 
                        self.dino.is_run = False 
                        self.dino.is_jump = False
                if event.type == pygame.KEYUP and not self.dino.is_jump: 
                    # 키 입력이 끝나면 다시 달리기 상태
                        self.dino.is_down = False 
                        self.dino.is_run = True 
                        self.dino.is_jump = False
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_LALT or event.key == pygame.K_RALT): # ALT 일시정지
                    self.paused = not self.paused
                    renpy.redraw(self, 0.1)
            if self.game_over: # 게임 종료 시 이벤트 무시
                raise renpy.IgnoreEvent()
    
    dino_game = DinosaurGame()
                
screen start_mini_game():
    text "시작하려면 스페이스 바를 누르세요..." color "#ffffff" size 40 xalign 0.5 yalign 0.5
    $ dino_game.__init__()
    key "K_SPACE" action Jump("dinosaur_game")


screen dino_runner_game():
    add dino_game

label dinosaur_game:
    scene bg
    call screen dino_runner_game

label game_over:
    "게임 오버... 당신의 점수는 ... [score]점 입니다."

    menu:
        "다시하기":
            call screen start_mini_game

        "끝내기":
            return