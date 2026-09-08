from app.infrastructure.database.models import (
    Area,
    Categoria,
    Division,
    Empresa,
    Fundo,
    Subcategoria,
)
from app.presentation.api.routes.catalogo_factory import crear_router_catalogo
from app.presentation.api.schemas.catalogos import (
    AreaCreate,
    AreaRead,
    CategoriaCreate,
    CategoriaRead,
    DivisionCreate,
    DivisionRead,
    EmpresaCreate,
    EmpresaRead,
    FundoCreate,
    FundoRead,
    SubcategoriaCreate,
    SubcategoriaRead,
)

router_empresas = crear_router_catalogo(
    prefix="/empresas",
    tag="Empresas",
    model=Empresa,
    read_schema=EmpresaRead,
    create_schema=EmpresaCreate,
)

router_divisiones = crear_router_catalogo(
    prefix="/divisiones",
    tag="Divisiones",
    model=Division,
    read_schema=DivisionRead,
    create_schema=DivisionCreate,
)

router_categorias = crear_router_catalogo(
    prefix="/categorias",
    tag="Categorías",
    model=Categoria,
    read_schema=CategoriaRead,
    create_schema=CategoriaCreate,
)

router_fundos = crear_router_catalogo(
    prefix="/fundos",
    tag="Fundos",
    model=Fundo,
    read_schema=FundoRead,
    create_schema=FundoCreate,
)

router_areas = crear_router_catalogo(
    prefix="/areas",
    tag="Áreas",
    model=Area,
    read_schema=AreaRead,
    create_schema=AreaCreate,
)

router_subcategorias = crear_router_catalogo(
    prefix="/subcategorias",
    tag="Subcategorías",
    model=Subcategoria,
    read_schema=SubcategoriaRead,
    create_schema=SubcategoriaCreate,
)

todos_los_routers_catalogo = [
    router_empresas,
    router_divisiones,
    router_categorias,
    router_fundos,
    router_areas,
    router_subcategorias,
]
