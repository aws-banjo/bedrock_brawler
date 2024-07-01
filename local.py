import asyncio

import boto3
import pygame

# from fighter import Fighter
from llm_fighter import LLMFighter


def get_model_display_name(model_id):

    model_ids = [
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "meta.llama3-8b-instruct-v1:0",
        "meta.llama3-70b-instruct-v1:0",
        "mistral.mistral-large-2402-v1:0",
        "mistral.mixtral-8x7b-instruct-v0:1",
    ]

    if model_id == model_ids[0]:
        return "Claude 3 Sonnet"
    elif model_id == model_ids[1]:
        return "Claude 3 Haiku"
    elif model_id == model_ids[2]:
        return "Llama 3 8B Instruct"
    elif model_id == model_ids[3]:
        return "Llama 3 70B Instruct"
    elif model_id == model_ids[4]:
        return "Mistral Large"
    elif model_id == model_ids[5]:
        return "Mixtral 8x7B"
    else:
        return "Unknown"


async def main():

    pygame.init()

    # create game window
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 600

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Model Brawl League")

    # set framerate
    clock = pygame.time.Clock()
    FPS = 60

    # define colours
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)

    # define game variables
    intro_count = 3
    last_count_update = pygame.time.get_ticks()
    score = [0, 0]  # player scores. [P1, P2]
    round_over = False
    ROUND_OVER_COOLDOWN = 2000

    # define fighter variables
    WARRIOR_SIZE = 162
    WARRIOR_SCALE = 4
    WARRIOR_OFFSET = [72, 56]
    WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
    WIZARD_SIZE = 250
    WIZARD_SCALE = 3
    WIZARD_OFFSET = [112, 107]
    WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]

    # load background image
    bg_image = pygame.image.load(
        "assets/images/background/background.jpg"
    ).convert_alpha()

    # load spritesheets
    warrior_sheet = pygame.image.load(
        "assets/images/warrior/Sprites/warrior.png"
    ).convert_alpha()
    wizard_sheet = pygame.image.load(
        "assets/images/wizard/Sprites/wizard.png"
    ).convert_alpha()

    # load vicory image
    victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()

    # define number of steps in each animation
    WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
    WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

    # define font
    count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
    score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)

    # function for drawing text
    def draw_text(text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))

    # function for drawing background
    def draw_bg():
        scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_bg, (0, 0))

    # function for drawing fighter health bars
    def draw_health_bar(health, x, y):
        ratio = health / 100
        pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
        pygame.draw.rect(screen, RED, (x, y, 400, 30))
        pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))

    def draw_timer(timer, x, y):

        if timer <= 0:
            timer = 0

        draw_text(f"{timer}", count_font, RED, x, y)

    # Pick Models here
    model_ids = [
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "meta.llama3-8b-instruct-v1:0",
        "meta.llama3-70b-instruct-v1:0",
        "mistral.mistral-large-2402-v1:0",
        "mistral.mixtral-8x7b-instruct-v0:1",
    ]

    model_1 = "anthropic.claude-3-sonnet-20240229-v1:0"
    system_prompt_1 = "You are a very defensive player"
    bedrock_runtime_1 = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-west-2",
    )

    display_name_1 = get_model_display_name(model_1)

    model_2 = "anthropic.claude-3-haiku-20240307-v1:0"
    system_prompt_2 = "You are a very aggressive player"
    bedrock_runtime_2 = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",
    )
    display_name_2 = get_model_display_name(model_2)

    fighter_1 = LLMFighter(
        1,
        200,
        310,
        False,
        WARRIOR_DATA,
        warrior_sheet,
        WARRIOR_ANIMATION_STEPS,
        model_1,
        system_prompt_1,
        bedrock_runtime_1,
    )

    fighter_2 = LLMFighter(
        2,
        700,
        310,
        True,
        WIZARD_DATA,
        wizard_sheet,
        WIZARD_ANIMATION_STEPS,
        model_2,
        system_prompt_2,
        bedrock_runtime_2,
    )

    # game loop
    run = True
    timer = 99
    while run:

        clock.tick(FPS)

        # draw background
        draw_bg()

        # show player stats
        draw_health_bar(fighter_1.health, 20, 20)
        draw_health_bar(fighter_2.health, 580, 20)
        draw_text(f"P1: {display_name_1} " + str(score[0]), score_font, RED, 20, 60)
        draw_text(f"P2: {display_name_2} " + str(score[1]), score_font, RED, 580, 60)
        draw_timer(timer, 460, 10)

        # update countdown
        if intro_count <= 0:
            # move fighters
            await fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_2, round_over)
            await fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_1, round_over)
        else:
            # display count timer
            draw_text(
                str(intro_count), count_font, RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3
            )
            # update count timer
            if (pygame.time.get_ticks() - last_count_update) >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()

        # update fighters
        fighter_1.update()
        fighter_2.update()

        # draw fighters
        fighter_1.draw(screen)
        fighter_2.draw(screen)

        # check for player defeat
        if round_over == False:
            if fighter_1.alive == False:
                score[1] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
            elif fighter_2.alive == False:
                score[0] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()

            if timer == 0:
                if fighter_1.health > fighter_2.health:
                    score[0] += 1
                elif fighter_2.health > fighter_1.health:
                    score[1] += 1
                else:
                    print("tie")
                    # no winner
                round_over = True
                round_over_time = pygame.time.get_ticks()

        else:
            # display victory image
            screen.blit(victory_img, (360, 150))
            if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                round_over = False
                intro_count = 3
                timer = 99
                fighter_1 = LLMFighter(
                    1,
                    200,
                    310,
                    False,
                    WARRIOR_DATA,
                    warrior_sheet,
                    WARRIOR_ANIMATION_STEPS,
                    model_1,
                    system_prompt_1,
                    bedrock_runtime_1,
                )

                fighter_2 = LLMFighter(
                    2,
                    700,
                    310,
                    True,
                    WIZARD_DATA,
                    wizard_sheet,
                    WIZARD_ANIMATION_STEPS,
                    model_2,
                    system_prompt_2,
                    bedrock_runtime_2,
                )

        # event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # count down timer for every 1 second of real time
        if (pygame.time.get_ticks() - last_count_update) >= 1000:
            timer -= 1
            last_count_update = pygame.time.get_ticks()

        # update display
        pygame.display.update()
        await asyncio.sleep(0)

    # exit pygame
    pygame.quit()


# This is the program entry point:
print("start game")
asyncio.run(main())
