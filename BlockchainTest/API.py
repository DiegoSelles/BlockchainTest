from uuid import uuid4

from flask import Flask, jsonify, request

from Blockchain import Blockchain

app = Flask(__name__)
# run_with_ngrok(app)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

#Crear la dirección del nodo en el puerto 5000
node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    """Minado de un nuevo bloque"""

    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address, receiver="Satoshi Nakamoto", amount=10)
    block = blockchain.create_block(proof, previous_hash)

    response = {'msg': "¡Has obtenido un nuevo bloque!",
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}

    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    """Obtención de la Blockchain"""
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}

    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    """Comprobación si la blockchain es válida"""

    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'msg': 'La cadena de bloques es valida'}
    else:
        response = {'msg': 'La cadena de bloques no es valida'}

    return jsonify(response), 200

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    """Añadir una nueva transacción a la cadena de bloques"""

    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Faltan algunos elementos de la transacción', 400

    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message' : f'La transacción será añadida al bloque {index}'}
    return jsonify(response), 201

@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No hay nodos para añadir', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message':'Todos los nodos han sido conectados.',
                    'total_nodes': list(blockchain.nodes)}

    return jsonify(response), 201


@app.route('/connect_node', methods=['GET'])
def replace_chain():
    """Remplazar la cadena por la más larga"""
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message':'Reemplazado, los nodos tenían cadenas diferentes.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message':'Ok.',
                    'new_chain': blockchain.chain}
    return jsonify(response), 200



app.run(host = '0.0.0.0', port = 5000)
