import entities
import db
# quick script to upload enemies to database.
try:
    grunt = entities.Enemy("Grunt",5,1,0,1,[],"aggro",5,2)
    grunt.init_no_class_enemy()
    db.insert_enemy(grunt)
except Exception as e:
    print(e)