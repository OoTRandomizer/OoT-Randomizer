# Function for adding hue to a greyscaled icon
def add_hue(image, color, tiff=False):
    start = 154 if tiff else 0
    for i in range(start, len(image), 4):
        try:
            for x in range(3):
                image[i+x] = int(((image[i+x]/255) * (color[x]/255)) * 255)
        except: 
            pass
    return image


# Function for adding belt to tunic
def add_belt(tunic, belt, tiff=False):
    start = 154 if tiff else 0
    for i in range(start, len(tunic), 4):
        try:
            if belt[i+3] != 0:
                alpha = belt[i+3] / 255
                for x in range(3):
                    tunic[i+x] = int((belt[i+x] * alpha) + (tunic[i+x] * (1 - alpha)))
        except:
            pass
    return tunic


# Function for putting tunic colours together
def generate_tunic_icon(color):
    with open('./data/icons/grey.tiff', 'rb') as grey_fil, open('./data/icons/belt.tiff', 'rb') as belt_fil:
        grey = list(grey_fil.read())
        belt = list(belt_fil.read())
        return add_belt(add_hue(grey, color, True), belt, True)[154:]


# TODO: Make these functions work

# def greyscale(image):
#     pass

# def extract_item_icon(rom, num):
#     item = rom.read_bytes(0x0074C000 + 0x1000*num, 0x1000)
#     return item

# def patch_item_icon(rom, num, item):
#     rom.write_bytes(0x0074C000 + 0x1000*num, item)
