from flask import request

def paginate(query, schema):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    per_page = min(per_page, 100)   

    result = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "data": schema.dump(result.items),
        "pagination": {
            "page": result.page,
            "per_page": result.per_page,
            "total": result.total,
            "total_pages": result.pages,
            "has_next": result.has_next,
            "has_prev": result.has_prev,
        },
    }