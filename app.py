from flask import Flask, request
from flask_pymongo import PyMongo
import os 
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)

str_de_conexao_mongo = os.getenv("progeficaz")
app.config["MONGO_URI"] = "mongodb+srv://admin:admin@cluster0.hmjqwho.mongodb.net/biblioteca_db"


mongo = PyMongo(app)

@app.route("/")
def home():
    return "API ProgEficaz"

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
    

##BICICLETAS
@app.route("/bicicletas", methods=['POST'])
def post_bike():
    data = request.json

    if "marca" not in data or "modelo" not in data or "cidade" not in data or "status" not in data:
        return {'erro': "todas as informações são obrigatórias"}, 400

    if data['status'] not in ['disponivel', 'em uso']:
        return {'erro': "status da bicicleta deve ser 'disponivel' ou 'em uso'"},  400

    bike = {
        'marca': data['marca'],
        'modelo': data['modelo'],
        'cidade': data['cidade'],
        'status': data['status']
    }

    result = mongo.db.bicicletas.insert_one(bike)

    return {"id": str(result.inserted_id)}, 201

@app.route("/bicicletas", methods=['GET'])
def get_all_bikes():
    bikes = mongo.db.bicicletas.find()

    output = []
    for bike in bikes:
        output.append({
            'id': str(bike['_id']),
            'marca': bike['marca'],
            'modelo': bike['modelo'],
            'cidade': bike['cidade'],
            'status': bike['status']
        })

    return {'bicicletas': output}, 200

@app.route("/bicicletas/<id_bike>", methods=['GET'])
def get_bike(id_bike):
    bike = mongo.db.bicicletas.find_one({"_id": ObjectId(id_bike)})
    if bike:
        return {
            'id': str(bike['_id']),
            'marca': bike['marca'],
            'modelo': bike['modelo'],
            'cidade': bike['cidade'],
            'status': bike['status']
        }
    else:
        return {'erro': 'Bicicleta não encontrada'}, 404
    
@app.route("/bicicletas/<id_bike>", methods=['PUT'])
def update_bike(id_bike):
    data = request.json

    if not data:
        return {'erro': "dados de atualização não fornecidos"}, 400

    # Verificar se a bicicleta existe
    bike = mongo.db.bicicletas.find_one({"_id": ObjectId(id_bike)})
    if not bike:
        return {'erro': 'Bicicleta não encontrada'}, 404

    for key in data:
        if key not in ['marca', 'modelo', 'cidade', 'status']:
            return {'erro': f'Campo {key} não pode ser atualizado'}, 400

    if 'status' in data and data['status'] not in ['disponivel', 'em uso']:
        return {'erro': "status da bicicleta deve ser 'disponivel' ou 'em uso'"}, 400

    mongo.db.bicicletas.update_one({"_id": ObjectId(id_bike)}, {"$set": data})

    return {'mensagem': 'Bicicleta atualizada com sucesso'}, 200

@app.route("/bicicletas/<id_bike>", methods=['DELETE'])
def delete_bike(id_bike):
    result = mongo.db.bicicletas.delete_one({"_id": ObjectId(id_bike)})
    if result.deleted_count == 1:
        return {'mensagem': 'Bicicleta deletada com sucesso'}, 200
    else:
        return {'erro': 'Bicicleta não encontrada'}, 404

##EMPRESTIMOS
@app.route("/emprestimos/usuarios/<id_usuario>/bicicletas/<id_bike>", methods=['POST'])
def post_loan(id_usuario, id_bike):
    # Verificar se a bicicleta está disponível
    bike = mongo.db.bicicletas.find_one({"_id": ObjectId(id_bike)})
    if not bike:
        return {'erro': 'Bicicleta não encontrada'}, 404

    if bike['status'] == 'em uso':
        return {'erro': 'Bicicleta já está alugada'}, 400

    # Registrar empréstimo
    emprestimo = {
        'id_usuario': id_usuario,
        'id_bicicleta': id_bike,
        'data_emprestimo': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    mongo.db.emprestimos.insert_one(emprestimo)

    # Atualizar status da bicicleta para em uso
    mongo.db.bicicletas.update_one({"_id": ObjectId(id_bike)}, {"$set": {"status": "em uso"}})

    return {'mensagem': 'Empréstimo registrado com sucesso'}, 201

@app.route("/emprestimos", methods=['GET'])
def get_all_loans():
    emprestimos = mongo.db.emprestimos.find()
    output = []
    for emprestimo in emprestimos:
        output.append({
            'id_usuario': str(emprestimo['id_usuario']),
            'id_bicicleta': str(emprestimo['id_bicicleta']),
            'id_emprestimo': str(emprestimo['_id'])
        })
    return {'emprestimos': output}

@app.route("/emprestimos/<id_emprestimo>", methods=['DELETE'])
def delete_loan(id_emprestimo):
    emprestimo = mongo.db.emprestimos.find_one({"_id": ObjectId(id_emprestimo)})
    if not emprestimo:
        return {'erro': 'Empréstimo não encontrado'}, 404

    # Atualizar status da bicicleta para disponível
    mongo.db.bicicletas.update_one({"_id": ObjectId(emprestimo['id_bicicleta'])}, {"$set": {"status": "disponivel"}})

    # Excluir empréstimo
    mongo.db.emprestimos.delete_one({"_id": ObjectId(id_emprestimo)})

    return {'mensagem': 'Empréstimo deletado com sucesso'}, 200


if __name__ == '__main__':
    app.run(debug=True)
