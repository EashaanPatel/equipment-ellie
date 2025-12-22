import argparse
import json
from pathlib import Path
from typing import Any

from equipment_service import EquipmentService
from people_service import PeopleService
from storage import JsonStore


def _build_store(data_file: str) -> JsonStore:
    return JsonStore(path=Path(data_file))


def _print_payload(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _handle_error(exc: Exception) -> None:
    raise SystemExit(str(exc))


def _add_equipment_commands(subparsers: argparse._SubParsersAction) -> None:
    equipment_parser = subparsers.add_parser("equipment", help="Manage equipment")
    equipment_subparsers = equipment_parser.add_subparsers(dest="equipment_command", required=True)

    add_parser = equipment_subparsers.add_parser("add", help="Add equipment")
    add_parser.add_argument("--name", required=True)
    add_parser.add_argument("--description")
    add_parser.add_argument("--status")
    add_parser.set_defaults(
        func=lambda args: _print_payload(
            EquipmentService(_build_store(args.data_file)).add_equipment(
                args.name, args.description, args.status
            )
        )
    )

    list_parser = equipment_subparsers.add_parser("list", help="List equipment")
    list_parser.set_defaults(
        func=lambda args: _print_payload(
            EquipmentService(_build_store(args.data_file)).list_equipment()
        )
    )

    get_parser = equipment_subparsers.add_parser("get", help="Get equipment by id")
    get_parser.add_argument("--id", required=True)
    get_parser.set_defaults(
        func=lambda args: _print_payload(
            EquipmentService(_build_store(args.data_file)).get_equipment(args.id)
        )
    )

    update_parser = equipment_subparsers.add_parser("update", help="Update equipment")
    update_parser.add_argument("--id", required=True)
    update_parser.add_argument("--name")
    update_parser.add_argument("--description")
    update_parser.add_argument("--status")
    update_parser.set_defaults(
        func=lambda args: _print_payload(
            EquipmentService(_build_store(args.data_file)).update_equipment(
                args.id, args.name, args.description, args.status
            )
        )
    )

    delete_parser = equipment_subparsers.add_parser("delete", help="Delete equipment")
    delete_parser.add_argument("--id", required=True)
    delete_parser.set_defaults(
        func=lambda args: EquipmentService(_build_store(args.data_file)).delete_equipment(
            args.id
        )
    )


def _add_people_commands(subparsers: argparse._SubParsersAction) -> None:
    people_parser = subparsers.add_parser("people", help="Manage people")
    people_subparsers = people_parser.add_subparsers(dest="people_command", required=True)

    add_parser = people_subparsers.add_parser("add", help="Add person")
    add_parser.add_argument("--name", required=True)
    add_parser.add_argument("--email")
    add_parser.add_argument("--role")
    add_parser.set_defaults(
        func=lambda args: _print_payload(
            PeopleService(_build_store(args.data_file)).add_person(
                args.name, args.email, args.role
            )
        )
    )

    list_parser = people_subparsers.add_parser("list", help="List people")
    list_parser.set_defaults(
        func=lambda args: _print_payload(
            PeopleService(_build_store(args.data_file)).list_people()
        )
    )

    get_parser = people_subparsers.add_parser("get", help="Get person by id")
    get_parser.add_argument("--id", required=True)
    get_parser.set_defaults(
        func=lambda args: _print_payload(
            PeopleService(_build_store(args.data_file)).get_person(args.id)
        )
    )

    update_parser = people_subparsers.add_parser("update", help="Update person")
    update_parser.add_argument("--id", required=True)
    update_parser.add_argument("--name")
    update_parser.add_argument("--email")
    update_parser.add_argument("--role")
    update_parser.set_defaults(
        func=lambda args: _print_payload(
            PeopleService(_build_store(args.data_file)).update_person(
                args.id, args.name, args.email, args.role
            )
        )
    )

    delete_parser = people_subparsers.add_parser("delete", help="Delete person")
    delete_parser.add_argument("--id", required=True)
    delete_parser.set_defaults(
        func=lambda args: PeopleService(_build_store(args.data_file)).delete_person(args.id)
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Equipment and people manager")
    parser.add_argument(
        "--data-file",
        default=str(Path(__file__).with_name("data.json")),
        help="Path to the JSON data store",
    )
    subparsers = parser.add_subparsers(dest="resource", required=True)
    _add_equipment_commands(subparsers)
    _add_people_commands(subparsers)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except (KeyError, ValueError) as exc:
        _handle_error(exc)


if __name__ == "__main__":
    main()
