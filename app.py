from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from dotenv import dotenv_values
from os import makedirs, path, rename, remove, listdir
from imagehash import dhash
from PIL import Image
from nudenet import NudeClassifier
from math import dist

classifier = NudeClassifier()

config = dotenv_values('.env')
for dirs in ["SAFE", "UNSAFE", "FUZZY", "TEMP"]:
  makedirs(config[dirs], exist_ok=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Imageprint(db.Model):
  id = db.Column(db.String(16), primary_key=True)
  name = db.Column(db.String(300), unique=False, nullable=False)
  folder = db.Column(db.String(10), nullable=False, default="TEMP")
  def __repr__(self):
      return f"{self.name} in {self.folder}, {self.id}"


@app.route('/', methods=['POST'])
def create():
  try:
    images = request.files.getlist("image[]")
    imgcount = 0
    for image in images:
      try:
        safetyname = safename(image.filename, config["TEMP"])
        savepath = path.join(config["TEMP"], safetyname)
        image.save(savepath)
        img_hash = hashedimage(savepath)
        try:
          img_print = savehash(img_hash, image.filename, "TEMP")
          category = identipy(savepath)
          newname = safename(image.filename, config[category])
          newpath = path.join(config[category], newname)
          rename(savepath, newpath)
          img_print.folder = category
          img_print.name = newname
          db.session.commit()
          print(newname, category)
        except exc.IntegrityError as err:
          db.session.rollback()
          dupeprint = Imageprint.query.get(img_hash)
          dupefile = printtopath(dupeprint)
          if path.getsize(savepath) > path.getsize(dupefile):
            rename(savepath, dupefile)
          else:
            remove(savepath)
          print(safetyname, dupeprint.name)
        imgcount += 1
      except Exception as err:
        print("Something's wrong")
      continue
    return {'images saved': imgcount}
  except KeyError as err:
    return {'error': 'invalid parameters'}, 400


def hashedimage(fullpath):
  image = Image.open(fullpath)
  return str(dhash(image))


def savehash(imghash, imgname, folder="TEMP"):
  imageprint = Imageprint(id=imghash, name=imgname, folder=folder)
  db.session.add(imageprint)
  db.session.commit()
  return imageprint


def printtopath(imageprint):
  filename = imageprint.name
  location = config[imageprint.folder]
  return path.join(location, filename)


def safename(filename, destination):
  name, ext = path.splitext(filename)
  count = 1
  while path.isfile(path.join(destination, filename)):
    filename = name[:200] + str(count) + ext
    count += 1
  return filename


def identipy(imagepath, prescision=0.2):
  result = classifier.classify(imagepath)[imagepath]
  diff = dist([result['safe']], [result['unsafe']])
  if diff < prescision:
    return "FUZZY"
  elif result['safe'] > result['unsafe']:
    return "SAFE"
  else:
    return "UNSAFE"


def genDB():
  db.drop_all()
  db.session.commit()
  db.create_all()
  for directory in ["SAFE", "UNSAFE", "FUZZY"]:
    location = config[directory]
    for image in listdir(location):
      _, ext = path.splitext(image)
      if ext.lower() in ('.jpg', '.jpeg', '.png', '.webp'):
        fullpath = path.join(location, image)
        h = hashedimage(fullpath)
        try: 
          savehash(h, image, directory)
        except exc.IntegrityError as err:
          db.session.rollback()
          dupeprint = Imageprint.query.get(h)
          dupefile = printtopath(dupeprint)
          if fullpath is not dupefile:
            if path.getsize(fullpath) > path.getsize(dupefile):
              rename(fullpath, dupefile)
            else:
              remove(fullpath)
        print(directory, image)
