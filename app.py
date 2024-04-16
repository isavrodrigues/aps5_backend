from flask import Flask, request, jsonify
import psycopg2


app = Flask("aps5")

@app.route('/usuarios', methods=['POST'])
def cadastra_usuario():
    nome = request.json['nome']
    cpf = request.json['cpf']
    data_nascimento = request.json['data_nascimento']

    if not nome or cpf or data_nascimento: 
        return {"erro" : "Todas as informações são obrigatórias"}, 400
    
    if cpf == '': 
        return {"erro" : "Insira seu CPF"}, 400 
    
    try:

        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (nome, cpf, data_nascimento) VALUES (%s, %s, %s)",
                (nome, cpf, data_nascimento))
        conn.commit()
    
    except psycopg2.Error as e:
        conn.rollback()
        return {"erro": str(e)}, 500
    finally:
        cur.close()
    
    resp = {
        "mensagem" : "Usuário cadastrado com sucesso",
        "usuario" : {
            "nome" : nome,
            "cpf" : cpf,
            "data_nascimento" : data_nascimento
        }
    }
    return resp, 201


@app.route('/usuarios', methods=['GET'])
def lista_usuarios():
    cur = conn.cursor()
    try:

        cur.execute ("SELECT * from usuarios")
        usuarios = cur.fetchall() 

    except psycopg2.Error as e:
        return {"erro": str(e)}, 500
    finally:
        cur.close()

    usuarios_lista = []
    for usuario in usuarios:
        usuarios_lista.append({

            "id": usuario[0],
            "nome": usuario[1],
            "cpf": usuario[2],
            "data_nascimento": usuario[3]
        })

    return usuarios_lista, 200



