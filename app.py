from flask import Flask, request
from flask_pymongo import PyMongo
import os 
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)

str_de_conexao_mongo = os.getenv("progeficaz")
app.config["MONGO_URI"] = str_de_conexao_mongo


mongo = PyMongo(app)

##USUARIOS 
@app.route("/usuarios", methods=['POST'])
def post_users():

    data = request.json

    if "nome" not in data or "cpf" not in data or "data_nascimento" not in data:
        return {'erro': "todos os campos são obrigatórios"}, 400
    
    usuarios = {
        'nome' : data['nome'],
        'cpf': data['cpf'],
        'data_nascimento': data['data_nascimento'],
    }
    
    existing_user = mongo.db.usuarios.find_one({"cpf": data["cpf"]})
    if existing_user:
        return ({'erro': "usuário com CPF já existe"}), 400

    result = mongo.db.usuarios.insert_one(usuarios)

    return {"id": str(result.inserted_id)}, 201

@app.route("/usuarios", methods=['GET'])
def get_all_users():
    usuarios = mongo.db.usuarios.find()

    output = []
    for usuario in usuarios:
        output.append({
            'id': str(usuario['_id']),
            'nome': usuario['nome'],
            'cpf': usuario['cpf'],
            'data_nascimento': usuario['data_nascimento']
        })

    return {'usuarios': output}, 200

@app.route("/usuarios/<id_usuario>", methods=['GET'])
def get_user(id_usuario):
    usuario = mongo.db.usuarios.find_one({"_id": ObjectId(id_usuario)})

    if usuario:
        return ({
            'id': str(usuario['_id']),
            'nome': usuario['nome'],
            'cpf': usuario['cpf'],
            'data_nascimento': usuario['data_nascimento']
        })
    else:
        return ({'erro': 'Usuário não encontrado'}), 404
    
@app.route("/usuarios/<id_usuario>", methods=['PUT'])
def update_user(id_usuario):
    data = request.json

    if not data:
        return {'erro': "dados de atualização não fornecidos"}, 400

    # Verificar se o usuário existe
    usuario = mongo.db.usuarios.find_one({"_id": ObjectId(id_usuario)})
    if not usuario:
        return {'erro': 'Usuário não encontrado'}, 404

    # Atualizar apenas o campo fornecido
    for key in data:
        if key not in ['nome', 'data_nascimento']:
            return {'erro': f'Campo {key} não pode ser atualizado'}, 400

        mongo.db.usuarios.update_one({"_id": ObjectId(id_usuario)}, {"$set": {key: data[key]}})

    return {'mensagem': 'Usuário atualizado com sucesso'} , 200

@app.route("/usuarios/<id_usuario>", methods=['DELETE'])
def delete_user(id_usuario):
    result = mongo.db.usuarios.delete_one({"_id": ObjectId(id_usuario)})

    if result.deleted_count == 1:
        return {'mensagem': 'Usuário deletado com sucesso'}, 200
    else:
        return {'erro': 'Usuário não encontrado'} , 404
    


