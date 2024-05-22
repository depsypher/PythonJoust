import pygame


def load_sliced_sprites(w, h, filename):
    # returns a list of image frames sliced from file
    results = []
    master_image = pygame.image.load(filename).convert_alpha()
    master_width, master_height = master_image.get_size()
    for i in range(int(master_width / w)):
        results.append(master_image.subsurface((i * w, 0, w, h)))
    return results


def load_sprite(x, y, w, h, scale, gap, frames, filename, color=None):
    # returns a list of image frames sliced from file at x, y
    results = []
    master_image = pygame.image.load(filename).convert_alpha()

    if color is not None:
        master_image.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)
        master_image.fill(color, special_flags=pygame.BLEND_RGBA_MIN)

    for i in range(frames):
        image = master_image.subsurface((x + i * w + (i * gap), y, w, h))
        if scale > 1:
            image = pygame.transform.scale_by(image, scale)
        results.append(image)
    return results


def load_image(x, y, w, h, scale, filename):
    master_image = pygame.image.load(filename).convert_alpha()
    image = master_image.subsurface((x, y, w, h))
    if scale > 1:
        image = pygame.transform.scale_by(image, scale)
    return image
