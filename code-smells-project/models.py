from database import get_db
from werkzeug.security import check_password_hash, generate_password_hash


def _produto(row):
    return {
        "id": row["id"], "nome": row["nome"], "descricao": row["descricao"],
        "preco": row["preco"], "estoque": row["estoque"], "categoria": row["categoria"],
        "ativo": row["ativo"], "criado_em": row["criado_em"],
    }


def get_todos_produtos():
    return [_produto(row) for row in get_db().execute("SELECT * FROM produtos").fetchall()]


def get_produto_por_id(id):
    row = get_db().execute("SELECT * FROM produtos WHERE id = ?", (id,)).fetchone()
    return _produto(row) if row else None


def criar_produto(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar_produto(id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, id),
    )
    db.commit()
    return True


def deletar_produto(id):
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (id,))
    db.commit()
    return True


def _usuario(row):
    return {
        "id": row["id"], "nome": row["nome"], "email": row["email"],
        "tipo": row["tipo"], "criado_em": row["criado_em"],
    }


def get_todos_usuarios():
    return [_usuario(row) for row in get_db().execute("SELECT * FROM usuarios").fetchall()]


def get_usuario_por_id(id):
    row = get_db().execute("SELECT * FROM usuarios WHERE id = ?", (id,)).fetchone()
    return _usuario(row) if row else None


def login_usuario(email, senha):
    row = get_db().execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    if row and not check_password_hash(row["senha"], senha):
        row = None
    return _usuario(row) if row else None


def criar_usuario(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, generate_password_hash(senha), tipo),
    )
    db.commit()
    return cursor.lastrowid


def criar_pedido(usuario_id, itens):
    db = get_db()
    total = 0
    produtos = []
    for item in itens:
        produto = db.execute(
            "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?",
            (item["produto_id"],),
        ).fetchone()
        if produto is None:
            return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": "Estoque insuficiente para " + produto["nome"]}
        produtos.append((item, produto))
        total += produto["preco"] * item["quantidade"]

    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
        (usuario_id, "pendente", total),
    )
    pedido_id = cursor.lastrowid
    for item, produto in produtos:
        db.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
        )
        db.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"]),
        )
    db.commit()
    return {"pedido_id": pedido_id, "total": total}


def _pedidos(query, params):
    db = get_db()
    pedidos = []
    for row in db.execute(query, params).fetchall():
        itens = db.execute(
            "SELECT i.produto_id, p.nome AS produto_nome, i.quantidade, i.preco_unitario "
            "FROM itens_pedido i LEFT JOIN produtos p ON p.id = i.produto_id "
            "WHERE i.pedido_id = ?",
            (row["id"],),
        ).fetchall()
        pedidos.append({
            "id": row["id"], "usuario_id": row["usuario_id"], "status": row["status"],
            "total": row["total"], "criado_em": row["criado_em"],
            "itens": [dict(item) for item in itens],
        })
    return pedidos


def get_pedidos_usuario(usuario_id):
    return _pedidos("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))


def get_todos_pedidos():
    return _pedidos("SELECT * FROM pedidos", ())


def relatorio_vendas():
    db = get_db()
    total_pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos").fetchone()[0]
    pendentes = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", ("pendente",)).fetchone()[0]
    aprovados = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", ("aprovado",)).fetchone()[0]
    cancelados = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", ("cancelado",)).fetchone()[0]
    desconto = 0
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    elif faturamento > 1000:
        desconto = faturamento * 0.02
    return {
        "total_pedidos": total_pedidos, "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2), "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes, "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos else 0,
    }


def atualizar_status_pedido(pedido_id, novo_status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()
    return True


def buscar_produtos(termo, categoria=None, preco_min=None, preco_max=None):
    clauses = []
    params = []
    if termo:
        clauses.append("(nome LIKE ? OR descricao LIKE ?)")
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        clauses.append("categoria = ?")
        params.append(categoria)
    if preco_min is not None:
        clauses.append("preco >= ?")
        params.append(preco_min)
    if preco_max is not None:
        clauses.append("preco <= ?")
        params.append(preco_max)
    query = "SELECT * FROM produtos"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    return [_produto(row) for row in get_db().execute(query, params).fetchall()]
