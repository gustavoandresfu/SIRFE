from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class TraceabilityMetadata:
    file_path: str
    class_name: str
    name: str
    start_line: int
    end_line: int
    node_type: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TraceabilityMetadata':
        return cls(
            file_path=data.get('file_path', ''),
            class_name=data.get('class_name', ''),
            name=data.get('name', ''),
            start_line=data.get('start_line', 0),
            end_line=data.get('end_line', 0),
            node_type=data.get('node_type', 'FunctionDef')
        )

@dataclass
class SemanticUnit:
    traceability: TraceabilityMetadata
    roles: List[Dict[str, Any]]        # e.g., [{"role": "VALIDATOR", "confidence": 0.9}]
    actions: List[Dict[str, Any]]      # e.g., [{"action": "ValidateUser", "confidence": 0.8}]
    inputs: List[str]
    outputs: List[str]
    dependencies: List[str]
    calls: List[str]
    state_changes: Dict[str, bool]     # e.g., {"persistent": True, "memory": True, "external": False}
    exceptions: List[str]
    preconditions: List[str]
    postconditions: List[str]
    domain: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "traceability": self.traceability.to_dict(),
            "roles": self.roles,
            "actions": self.actions,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "dependencies": self.dependencies,
            "calls": self.calls,
            "state_changes": self.state_changes,
            "exceptions": self.exceptions,
            "preconditions": self.preconditions,
            "postconditions": self.postconditions,
            "domain": self.domain
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SemanticUnit':
        return cls(
            traceability=TraceabilityMetadata.from_dict(data.get('traceability', {})),
            roles=data.get('roles', []),
            actions=data.get('actions', []),
            inputs=data.get('inputs', []),
            outputs=data.get('outputs', []),
            dependencies=data.get('dependencies', []),
            calls=data.get('calls', []),
            state_changes=data.get('state_changes', {"persistent": False, "memory": False, "external": False}),
            exceptions=data.get('exceptions', []),
            preconditions=data.get('preconditions', []),
            postconditions=data.get('postconditions', []),
            domain=data.get('domain', 'GENERIC')
        )

@dataclass
class Cluster:
    id: int
    units: List[SemanticUnit]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "units": [u.to_dict() for u in self.units]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Cluster':
        # Conservar compatibilidad si el JSON viejo usaba "methods" en vez de "units"
        units_data = data.get('units', data.get('methods', []))
        return cls(
            id=data.get('id', 0),
            units=[SemanticUnit.from_dict(u) for u in units_data]
        )

@dataclass
class GherkinScenario:
    dado: str
    cuando: str
    entonces: List[str]
    y: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GherkinScenario':
        return cls(
            dado=data.get('dado', ''),
            cuando=data.get('cuando', ''),
            entonces=data.get('entonces', []),
            y=data.get('y', '')
        )

@dataclass
class TechnicalSupport:
    cantidad_unidades: int
    unidades: List[str]  # Identificadores legibles (ej., "Clase.metodo")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TechnicalSupport':
        # Compatibilidad con campos antiguos "cantidad_metodos" y "metodos"
        unidades = data.get('unidades', data.get('metodos', []))
        cantidad = data.get('cantidad_unidades', data.get('cantidad_metodos', len(unidades)))
        return cls(
            cantidad_unidades=cantidad,
            unidades=unidades
        )

@dataclass
class FunctionalCapability:
    id: str
    titulo: str
    historia_usuario: str
    escenario_gherkin_sintetizado: GherkinScenario
    sustento_tecnico: TechnicalSupport

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "historia_usuario": self.historia_usuario,
            "escenario_gherkin_sintetizado": self.escenario_gherkin_sintetizado.to_dict(),
            "sustento_tecnico": self.sustento_tecnico.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FunctionalCapability':
        return cls(
            id=data.get('id', ''),
            titulo=data.get('titulo', ''),
            historia_usuario=data.get('historia_usuario', data.get('story', '')),
            escenario_gherkin_sintetizado=GherkinScenario.from_dict(data.get('escenario_gherkin_sintetizado', {})),
            sustento_tecnico=TechnicalSupport.from_dict(data.get('sustento_tecnico', {}))
        )

@dataclass
class FunctionalSpecification:
    proyecto: str
    metodologia: str
    capacidades_funcionales: List[FunctionalCapability]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proyecto": self.proyecto,
            "metodologia": self.metodologia,
            "capacidades_funcionales": [c.to_dict() for c in self.capacidades_funcionales]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FunctionalSpecification':
        return cls(
            proyecto=data.get('proyecto', ''),
            metodologia=data.get('metodologia', ''),
            capacidades_funcionales=[FunctionalCapability.from_dict(c) for c in data.get('capacidades_funcionales', [])]
        )
