import unittest
import pygame
# استيراد الفئات من ملف اللعبة الرئيسي (افترضنا أن اسمه main.py)
# يمكنك حفظ هذا الكود في ملف جديد بنفس المجلد وتشغيله
from main import Player, Bullet, Chicken, Egg

class TestChickenInvaders(unittest.TestCase):

    def setUp(self):
        """إعداد البيئة المبدئية قبل كل اختبار"""
        pygame.init()
        self.player = Player()

    def test_player_initial_state(self):
        """اختبار القيم الافتراضية للاعب"""
        self.assertEqual(self.player.weapon_level, 1)
        self.assertEqual(self.player.score, 0)

    def test_player_movement(self):
        """اختبار حركة المركبة"""
        initial_x = self.player.x
        # محاكاة الضغط على زر السهم الأيمن
        keys = {pygame.K_LEFT: False, pygame.K_RIGHT: True, pygame.K_UP: False, pygame.K_DOWN: False}
        self.player.move(keys)
        self.assertGreater(self.player.x, initial_x)

    def test_player_shooting(self):
        """اختبار عدد الطلقات الخارجة حسب مستوى السلاح"""
        # المستوى الأول: طلقة واحدة
        bullets_lvl1 = self.player.shoot(level=1)
        self.assertEqual(len(bullets_lvl1), 1)

        # المستوى الثالث: 3 طلقات
        self.player.weapon_level = 3
        bullets_lvl3 = self.player.shoot(level=1)
        self.assertEqual(len(bullets_lvl3), 3)

    def test_chicken_initialization(self):
        """اختبار إنشاء الفراخ حسب المستوى"""
        chicken = Chicken(level=5)
        self.assertEqual(chicken.level, 5)
        self.assertGreater(chicken.speed_y, 1) # السرعة تزداد مع المستوى

    def tearDown(self):
        pygame.quit()

if __name__ == '__main__':
    unittest.main()