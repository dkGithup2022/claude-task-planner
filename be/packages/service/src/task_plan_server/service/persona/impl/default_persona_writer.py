import logging

from task_plan_server.exception.persona.persona_name_duplicated_exception import (
    PersonaNameDuplicatedException,
)
from task_plan_server.exception.persona.persona_not_found_exception import PersonaNotFoundException
from task_plan_server.infrastructure.persona.persona_repository import PersonaRepository
from task_plan_server.model.persona.persona import Persona
from task_plan_server.model.persona.persona_identity import PersonaIdentity
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.persona_create_command import PersonaCreateCommand
from ..dto.persona_update_command import PersonaUpdateCommand
from ..persona_writer import PersonaWriter

logger = logging.getLogger(__name__)


class DefaultPersonaWriter(PersonaWriter):
    def __init__(self, tx: TransactionManager, repository: PersonaRepository) -> None:
        self.tx = tx
        self._repository = repository

    @transactional
    def create(self, command: PersonaCreateCommand) -> PersonaIdentity:
        if self._repository.exists_by_name(command.name, exclude=None):
            raise PersonaNameDuplicatedException(command.name)
        saved = self._repository.save(Persona.create(command.name, command.description))
        assert saved.persona_id is not None
        logger.info("Persona created: id=%s, name=%s", saved.persona_id, saved.name)
        return PersonaIdentity(saved.persona_id)

    @transactional
    def update(self, command: PersonaUpdateCommand) -> Persona:
        identity = PersonaIdentity(command.persona_id)
        existing = self._repository.find_write_by_id(identity)
        if existing is None:
            raise PersonaNotFoundException(f"persona not found: {command.persona_id}")
        name = existing.name if command.name is None else command.name
        if name != existing.name and self._repository.exists_by_name(name, exclude=identity):
            raise PersonaNameDuplicatedException(name)
        description = existing.description if command.description is None else command.description
        saved = self._repository.save(existing.with_profile(name, description))
        logger.info("Persona updated: id=%s", saved.persona_id)
        return saved

    @transactional
    def delete(self, identity: PersonaIdentity) -> None:
        if self._repository.find_write_by_id(identity) is None:
            raise PersonaNotFoundException(f"persona not found: {identity.persona_id}")
        self._repository.delete_by_id(identity)
        logger.info("Persona deleted: id=%s", identity.persona_id)
