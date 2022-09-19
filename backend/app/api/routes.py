import pathlib
import importlib


def get_subrouters(directory):
    routers = []

    package_parts = directory.parts[len(pathlib.Path.cwd().parts) :]
    parent_router = None

    try:
        pymod_file = ".".join(package_parts)
        pymod = importlib.import_module(pymod_file)

        if "router" in dir(pymod):
            parent_router = pymod.router
            routers.append(parent_router)
    except Exception as e:
        print("error", e)
        return routers

    subrouters = []
    for module in directory.iterdir():

        if "__" == module.name[:2]:
            continue

        if module.match("*.py"):
            pymod_file = f"{'.'.join(package_parts)}.{module.stem}"
            pymod = importlib.import_module(pymod_file)

            if "router" in dir(pymod):
                subrouters.append(pymod.router)

        elif module.is_dir():
            subrouters.extend(get_subrouters(module))

    for router in subrouters:
        if parent_router:
            parent_router.include_router(router)
        else:
            routers.append(router)

    return routers


def register_routers(app, root="app/api/"):
    prefix = ""
    parent = pathlib.Path(root).absolute()
    routers = get_subrouters(parent)

    for router in routers:
        app.include_router(router, prefix=prefix)
