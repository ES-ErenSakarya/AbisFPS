from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

window.title = "Python 3D FPS Oyunu - Dust2 Arena"
window.borderless = False
window.exit_button.enabled = False
window.fps_counter.enabled = True

# Gökyüzü ve Ortam Aydınlatması (Derinlik ve görünürlük için şart)
Sky(color=color.rgb(135, 206, 235)) # Açık mavi gökyüzü

sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))
sun.color = color.rgb(255, 255, 240)
AmbientLight(color=color.rgba(180, 180, 180, 255))

# ==========================================
# GÖRÜNÜR VE DOKULU DUST2 / ÇÖL ARENASI
# ==========================================

# 1. Ana Kum Zemin (texture='white_cube' ile ışığı doğru yansıtır ve net görünür)
ground = Entity(model='cube', texture='white_cube', scale=(80, 1, 80), y=-0.5, color=color.rgb(210, 180, 140), collider='box')

# 2. Çim Alanlar
grass_1 = Entity(model='cube', texture='white_cube', scale=(12, 1.1, 8), position=(-25, -0.4, 25), color=color.rgb(60, 160, 60), collider='box')
grass_2 = Entity(model='cube', texture='white_cube', scale=(10, 1.1, 10), position=(25, -0.4, -25), color=color.rgb(50, 140, 50), collider='box')
grass_3 = Entity(model='cube', texture='white_cube', scale=(6, 1.1, 15), position=(-28, -0.4, -10), color=color.rgb(70, 170, 70), collider='box')

# 3. Dış Sınır Duvarları
wall_color = color.rgb(230, 205, 170)
wall_north = Entity(model='cube', texture='white_cube', scale=(80, 6, 2), position=(0, 2.5, 40), color=wall_color, collider='box')
wall_south = Entity(model='cube', texture='white_cube', scale=(80, 6, 2), position=(0, 2.5, -40), color=wall_color, collider='box')
wall_east = Entity(model='cube', texture='white_cube', scale=(2, 6, 80), position=(40, 2.5, 0), color=wall_color, collider='box')
wall_west = Entity(model='cube', texture='white_cube', scale=(2, 6, 80), position=(-40, 2.5, 0), color=wall_color, collider='box')

# 4. Taktiksel Binalar ve Siperler
long_wall = Entity(model='cube', texture='white_cube', scale=(3, 5, 25), position=(18, 2, 5), color=wall_color, collider='box')

box_color = color.rgb(150, 100, 50)
crate_1 = Entity(model='cube', texture='white_cube', scale=(3, 3, 3), position=(8, 1, 8), color=box_color, collider='box')
crate_2 = Entity(model='cube', texture='white_cube', scale=(3, 3, 3), position=(11, 1, 8), color=box_color, collider='box')
crate_3 = Entity(model='cube', texture='white_cube', scale=(4, 2, 2), position=(-12, 1, -8), color=box_color, collider='box')
crate_4 = Entity(model='cube', texture='white_cube', scale=(2, 4, 2), position=(-15, 2, 12), color=box_color, collider='box')

cover_1 = Entity(model='cube', texture='white_cube', scale=(8, 3, 1.5), position=(0, 1.5, -15), color=wall_color, collider='box')
cover_2 = Entity(model='cube', texture='white_cube', scale=(1.5, 3, 8), position=(-18, 1.5, 0), color=wall_color, collider='box')

print("Görselleştirilmiş Dust2 haritası başarıyla yüklendi!")

# ==========================================
# OYUNCU VE SİLAH SİSTEMİ
# ==========================================
player = FirstPersonController()
player.x = 0
player.y = 2
player.z = 0
player.speed = 8
player.jump_height = 1.2
player.gravity = 0.5
player.cursor.visible = False

# Arayüz
crosshair = Text(text='+', origin=(0, 0), scale=2, color=color.red)
ammo_text = Text(text='Mermi: 10 / 30', position=(-0.85, 0.42), scale=1.2, color=color.white)

# Silahı Kameraya Bağlama
try:
    pistol = Entity(
        model='pistol.glb',
        parent=camera,
        position=(0.2, -0.12, 0.35),
        scale=(0.001, 0.001, 0.001),
        rotation=(0, 180, 0)
    )
    print("Silah başarıyla yüklendi!")
except Exception as e:
    print("Silah yüklenemedi:", e)
    pistol = None

# Silah Mekanik Değişkenleri
current_ammo = 10
magazine_size = 10
reserve_ammo = 30
is_reloading = False
is_ads = False

normal_pos = Vec3(0.2, -0.12, 0.35)
ads_pos = Vec3(0, -0.08, 0.3)

def update():
    global is_ads
    
    # Nişan Alma (ADS)
    if held_keys['right mouse'] and not is_reloading:
        if not is_ads:
            is_ads = True
            camera.fov = 55
            if pistol:
                pistol.position = ads_pos
    else:
        if is_ads and not is_reloading:
            is_ads = False
            camera.fov = 90
            if pistol:
                pistol.position = normal_pos

def input(key):
    global current_ammo, reserve_ammo, is_reloading
    
    # Sol Tık: Ateş Etme
    if key == 'left mouse down' and not is_reloading:
        if current_ammo > 0:
            current_ammo -= 1
            ammo_text.text = f'Mermi: {current_ammo} / {reserve_ammo}'
            
            if pistol:
                target_recoil = ads_pos if is_ads else normal_pos
                pistol.position += Vec3(0, 0.005, -0.02)
                invoke(setattr, pistol, 'position', target_recoil, delay=0.08)
        else:
            ammo_text.text = "ŞARJÖR BİTTİ! (R)"

    # R Tuşu: Gerçekçi Taktiksel Reload
    elif key == 'r' and not is_reloading:
        if reserve_ammo > 0 and current_ammo < magazine_size:
            start_realistic_reload()

def start_realistic_reload():
    global current_ammo, reserve_ammo, is_reloading, is_ads
    is_reloading = True
    ammo_text.text = "Şarjör Değiştiriliyor..."
    
    if is_ads:
        is_ads = False
        camera.fov = 90

    if pistol:
        pistol.animate_position(Vec3(0.18, -0.32, 0.38), duration=0.15, curve=curve.in_out_sine)
        pistol.animate_rotation(Vec3(25, 185, -20), duration=0.15, curve=curve.in_out_sine)
        
        def step2():
            pistol.animate_position(Vec3(0.18, -0.36, 0.4), duration=0.1, curve=curve.in_out_sine)
        invoke(step2, delay=0.15)
        
        def step3():
            global current_ammo, reserve_ammo
            needed = magazine_size - current_ammo
            if reserve_ammo >= needed:
                reserve_ammo -= needed
                current_ammo = magazine_size
            else:
                current_ammo += reserve_ammo
                reserve_ammo = 0
            ammo_text.text = f'Mermi: {current_ammo} / {reserve_ammo}'
            pistol.animate_position(Vec3(0.18, -0.28, 0.35), duration=0.1, curve=curve.in_out_sine)
        invoke(step3, delay=0.25)
        
        def step4():
            pistol.animate_position(Vec3(0.2, -0.15, 0.32), duration=0.1, curve=curve.in_out_sine)
        invoke(step4, delay=0.35)
        
        def step5():
            global is_reloading
            pistol.animate_position(normal_pos, duration=0.2, curve=curve.in_out_sine)
            pistol.animate_rotation(Vec3(0, 180, 0), duration=0.2, curve=curve.in_out_sine)
            is_reloading = False
            ammo_text.text = f'Mermi: {current_ammo} / {reserve_ammo}'
        invoke(step5, delay=0.45)

app.run()

# Güncelleme testi yapıldx