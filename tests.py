import logging 
from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User

class UserModelCase(unittest.TestCase):
  def setUp(self):
    self.add_fake_user(TF="TF99998", country="ESP",department="TisGF",activeUntil="1900-01-01",certPwd="TF99998",fullName="Arek Malysz")
    self.add_fake_user(TF="TF99999", country="ESP",department="TisGF",activeUntil="1900-01-01",certPwd="TF99999", fullName="Robert Korzeniowski")
    self.add_fake_user(TF="TF99997", country="ESP",department="TisGF",activeUntil="1900-01-01",certPwd="TF99997", fullName="Robert Lewandowski")
    self.add_fake_user(TF="TF99996", country="ESP",department="TisGF",activeUntil="1900-01-01",certPwd="TF99996", fullName="Lukasz Piszczek")

  def tearDown(self):
    self.delete_fake_user(TF="TF99998", country="ESP")
    self.delete_fake_user(TF="TF99999", country="ESP")
    self.delete_fake_user(TF="TF99990", country="CHI")
    self.delete_fake_user(TF="TF99991", country="ESP")
    self.delete_fake_user(TF="TF99997", country="ESP")
    self.delete_fake_user(TF="TF99996", country="ESP")

  def test_password_hashing(self):
    u = User(my_tif="TF99999")
    u.set_password("dupa")
    self.assertFalse(u.check_password('choj'))
    self.assertTrue(u.check_password('dupa'))

  def test_follow(self):
    u1 = User(my_tif="TF99999")
    u2 = User(my_tif="TF99998")

    self.assertEqual(u1.am_following, ["TF99999"])
    self.assertEqual(u2.am_following, ["TF99998"])

    u1.follow(u2)
    self.assertTrue(u1.is_following(u2.TIF))
    self.assertEqual(len(u1.get_am_following_without_me()),1)
    
    self.assertEqual(User(u1.get_am_following_without_me()[0]).fullName, 'Arek Malysz')
    self.assertEqual(len(u2.get_am_followed_by_without_me()), 1)
    self.assertEqual(User(u2.get_am_followed_by_without_me()[0]).fullName, 'Robert Korzeniowski')

    u1.unfollow(u2)
    self.assertFalse(u1.is_following(u2.TIF))
    self.assertEqual(len(u1.get_am_following_without_me()),0)
    self.assertEqual(len(u2.get_am_followed_by_without_me()),0)

  def test_follow_posts(self):
    #create 4 users
    u1 = User(my_tif="TF99999")
    u2 = User(my_tif="TF99998")
    u3 = User(my_tif="TF99997")
    u4 = User(my_tif="TF99996")

    u1.add_post("post of u1")
    u2.add_post("post of u2")
    u3.add_post("post of u3")
    u4.add_post("post of u4")

    u1.follow(u2)
    u1.follow(u4)
    u2.follow(u3)
    u3.follow(u4)
    
    f1 = u1.followed_posts_bodies()
    f2 = u2.followed_posts_bodies()
    f3 = u3.followed_posts_bodies()
    f4 = u4.followed_posts_bodies()
    self.assertEqual(f1, ["post of u1","post of u2","post of u4"])
    self.assertEqual(f2, ["post of u2","post of u3"])
    self.assertEqual(f3, ["post of u3","post of u4"])
    logging.warning(f4)
    self.assertEqual(f4, ["post of u4"])

  def add_fake_user(self, TF, country, department, fullName, activeUntil, certPwd):
    db.save_to_db("insert into tblUsers (TIF, country, department, fullName, activeUntil, certPwd) values ('" + TF + "','" + country + "','" + department + "','" + fullName + "','" + activeUntil + "', ENCRYPTBYASYMKEY(ASYMKEY_ID('ClaveAsym'), '" + certPwd + "'))")
    db.save_to_db("insert into RRHH_followers (followerTF, followedTF) values('" + str(TF) + "','" + str(TF) + "')")

  def delete_fake_user(self, TF, country):
    db.save_to_db("delete from RRHH_blogPosts where TF = '" + TF + "'")
    db.save_to_db("delete from RRHH_followers where followerTF = '" + TF + "' or followedTF = '" + TF + "'")
    db.save_to_db("delete from tblUsers where country = '" + country + "' and TIF = '" + TF + "'")

if __name__ == '__main__':
    unittest.main(verbosity=2)