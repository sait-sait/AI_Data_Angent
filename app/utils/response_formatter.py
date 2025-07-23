def format_response(columns, rows):
    result = [dict(zip(columns, row)) for row in rows]
    return {"results": result}
