from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class MethodIR:
    role: str
    effect: str
    op_type: str
    context: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'MethodIR':
        return cls(
            role=data.get('role', 'EXTRACTOR'),
            effect=data.get('effect', 'STABLE'),
            op_type=data.get('op_type', 'SEQUENTIAL'),
            context=data.get('context', 'GENERIC')
        )

@dataclass
class MethodMetadata:
    class_name: str  # maps to "class" in JSON
    method: str
    ir: MethodIR

    def to_dict(self) -> Dict[str, Any]:
        return {
            "class": self.class_name,
            "method": self.method,
            "ir": self.ir.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MethodMetadata':
        return cls(
            class_name=data.get('class', 'GenericClass'),
            method=data.get('method', 'generic_method'),
            ir=MethodIR.from_dict(data.get('ir', {}))
        )

@dataclass
class Cluster:
    id: int
    methods: List[MethodMetadata]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "methods": [m.to_dict() for m in self.methods]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Cluster':
        return cls(
            id=data.get('id', 0),
            methods=[MethodMetadata.from_dict(m) for m in data.get('methods', [])]
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
    cantidad_metodos: int
    metodos: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TechnicalSupport':
        return cls(
            cantidad_metodos=data.get('cantidad_metodos', 0),
            metodos=data.get('metodos', [])
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
