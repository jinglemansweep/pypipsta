from helpers import Pipsta

pipsta = Pipsta()
pipsta.tprint("TALL", font=Pipsta.FONT_TALL)
pipsta.tprint("WIDE", font=Pipsta.FONT_WIDE)
pipsta.tprint("""It's close to midnight and something evil's
lurking In the dark . Under the moonlight you see a sight
that almost stops. Your heart You try to scream, but terror
takes the sound before""", wrap=True)
