# -*- coding: utf-8 -*-
import os
import re
from enum import auto
from enum import Enum
from functools import partial
from functools import reduce
from itertools import chain
from typing import Any
from typing import Callable
from typing import Dict
from typing import IO
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Type
from typing import TypeVar


flatten = chain.from_iterable

# Resources

Property = Tuple[str, Any]
T = TypeVar('T', bound='Resource')
ParsingRule = Callable[[str], Optional[Property]]
ValidationRule = Callable[[T], Optional[str]]


def parse(line: str, rules: Iterable[ParsingRule]):
    """Parse properties out from a line based on some parsing rules"""
    properties = [rule(line) for rule in rules]
    return [prop for prop in properties if prop]


def validate(resource: T, rules: Iterable[ValidationRule]) -> Optional[str]:
    """Validate terraform resource and warn in case of violations
    :return: warning message to show
    """
    violations = [rule(resource) for rule in rules]
    violations = [v for v in violations if v]
    if violations:
        return "\n\t".join((f"{resource.type} - {resource.name}:", *violations))
    return None


class Resource:
    parsing_rules: Set[ParsingRule] = set()
    validation_rules: Set[ValidationRule] = set()

    def __init__(self, type: str, name: str) -> None:
        self.type = type
        self.name = name

    @classmethod
    def from_config(self, config: List[str]) -> 'Resource':
        raise NotImplementedError("Resource cannot be instantiated directly from config")

    @classmethod
    def register_parsing_rule(cls, rule: ParsingRule) -> None:
        cls.parsing_rules = cls.parsing_rules | {rule}

    @classmethod
    def get_parsing_rules(cls) -> Set[ParsingRule]:
        return Resource.parsing_rules

    @classmethod
    def register_validation_rule(cls, rule: ValidationRule) -> None:
        cls.validation_rules = cls.validation_rules | {rule}

    def get_validation_rules(self) -> Set[ValidationRule]:
        return Resource.validation_rules

    @classmethod
    def parse(cls, line: str) -> List[Property]:
        return parse(line, Resource.parsing_rules)

    @classmethod
    def parse_config(cls, config: List[str]) -> List[Property]:
        return list(flatten(cls.parse(line) for line in config))

    def validate(self) -> Optional[str]:
        return validate(self, Resource.validation_rules)


class SignalFlowResource(Resource):
    parsing_rules: Set[ParsingRule] = set()
    validation_rules: Set[ValidationRule] = set()

    def __init__(self, type: str, name: str, program_text: str, max_delay: Optional[int]=None) -> None:
        super().__init__(type, name)
        self.program_text = program_text
        self.max_delay = max_delay

    @classmethod
    def from_config(self, config: List[str]) -> 'SignalFlowResource':
        raise NotImplementedError("SignalFlowResource cannot be instantiated directly from config")

    @classmethod
    def get_parsing_rules(cls) -> Set[ParsingRule]:
        return SignalFlowResource.parsing_rules | super().get_parsing_rules()

    def get_validation_rules(self) -> Set[ValidationRule]:
        return SignalFlowResource.validation_rules | super().get_validation_rules()

    @classmethod
    def parse(cls, line: str) -> List[Property]:
        return parse(line, cls.get_parsing_rules())

    def validate(self) -> Optional[str]:
        return validate(self, self.get_validation_rules())


class Detector(SignalFlowResource):
    parsing_rules: Set[ParsingRule] = set()
    validation_rules: Set[ValidationRule] = set()

    def __init__(self, name: str, program_text: str, max_delay: Optional[int]=None, detect_labels: Optional[Set[str]]=None) -> None:
        super().__init__("detector", name, program_text, max_delay)
        self.detect_labels = detect_labels or set()

    @classmethod
    def from_config(cls, config: List[str]) -> 'Detector':
        properties = cls.parse_config(config)
        detect_labels = {value for key, value in properties if key == "detect_label"}
        fields = dict(properties)
        try:
            return Detector(fields["name"], fields["program_text"], fields.get("max_delay"), detect_labels)
        except KeyError as e:
            raise ValueError(f"Required field '{e.args[0]}' missing for detector") from e

    @classmethod
    def get_parsing_rules(cls) -> Set[ParsingRule]:
        return Detector.parsing_rules | super().get_parsing_rules()

    def get_validation_rules(self) -> Set[ValidationRule]:
        return Detector.validation_rules | super().get_validation_rules()

    @classmethod
    def parse(cls, line: str) -> List[Property]:
        return parse(line, cls.get_parsing_rules())

    def validate(self) -> Optional[str]:
        return validate(self, self.get_validation_rules())


class Chart(SignalFlowResource):
    parsing_rules: Set[ParsingRule] = set()
    validation_rules: Set[ValidationRule] = set()

    def __init__(self, name: str, program_text: str, max_delay: Optional[int]=None) -> None:
        super().__init__("chart", name, program_text, max_delay)

    @classmethod
    def from_config(cls, config: List[str]) -> 'Chart':
        fields = dict(cls.parse_config(config))
        try:
            return Chart(fields["name"], fields["program_text"], fields.get("max_delay"))
        except KeyError as e:
            raise ValueError(f"Required field '{e.args[0]}' missing for chart") from e

    @classmethod
    def get_parsing_rules(cls) -> Set[ParsingRule]:
        return Chart.parsing_rules | super().get_parsing_rules()

    def get_validation_rules(self) -> Set[ValidationRule]:
        return Chart.validation_rules | super().get_validation_rules()

    @classmethod
    def parse(cls, line: str) -> List[Property]:
        return parse(line, cls.get_parsing_rules())

    def validate(self) -> Optional[str]:
        return validate(self, self.get_validation_rules())


class Dashboard(Resource):
    parsing_rules: Set[ParsingRule] = set()
    validation_rules: Set[ValidationRule] = set()

    def __init__(self, name: str) -> None:
        super().__init__("dashboard", name)

    @classmethod
    def from_config(cls, config: List[str]) -> 'Dashboard':
        fields = dict(cls.parse_config(config))
        try:
            return Dashboard(fields["name"])
        except KeyError as e:
            raise ValueError(f"Required field '{e.args[0]}' missing for dashboard") from e

    @classmethod
    def get_parsing_rules(cls) -> Set[ParsingRule]:
        return Dashboard.parsing_rules | super().get_parsing_rules()

    def get_validation_rules(self) -> Set[ValidationRule]:
        return Dashboard.validation_rules | super().get_validation_rules()

    @classmethod
    def parse(cls, line: str) -> List[Property]:
        return parse(line, cls.get_parsing_rules())

    def validate(self) -> Optional[str]:
        return validate(self, self.get_validation_rules())


class DashboardGroup(Resource):
    parsing_rules: Set[ParsingRule] = set()
    validation_rules: Set[ValidationRule] = set()

    def __init__(self, name: str) -> None:
        super().__init__("dashboard_group", name)

    @classmethod
    def from_config(cls, config: List[str]) -> 'DashboardGroup':
        fields = dict(cls.parse_config(config))
        try:
            return DashboardGroup(fields["name"])
        except KeyError as e:
            raise ValueError(f"Required field '{e.args[0]}' missing for dashboard group") from e

    @classmethod
    def get_parsing_rules(cls) -> Set[ParsingRule]:
        return DashboardGroup.parsing_rules | super().get_parsing_rules()

    def get_validation_rules(self) -> Set[ValidationRule]:
        return DashboardGroup.validation_rules | super().get_validation_rules()

    @classmethod
    def parse(cls, line: str) -> List[Property]:
        return parse(line, cls.get_parsing_rules())

    def validate(self) -> Optional[str]:
        return validate(self, self.get_validation_rules())


AVAILABLE_RESOURCES: Dict[str, Type[Resource]] = {
    "signalform_detector": Detector,
    "signalform_time_chart": Chart,
    "signalform_heatmap_chart": Chart,
    "signalform_single_value_chart": Chart,
    "signalform_list_chart": Chart,
    "signalform_text_chart": Chart,
    "signalform_dashboard": Dashboard,
    "signalform_dashboard_group": DashboardGroup,
}


def find_and_make_resource(available_resources: Dict[str, Type[Resource]], res_type: str, lines: List[str]) -> Resource:
    """Make a resource out of Terraform configs
    :raise: ValueError if unrecognized resource
    """
    try:
        return available_resources[res_type].from_config(lines)
    except KeyError:
        raise ValueError(f"Unrecognized resource type: {res_type}")


RESOURCE_RE = re.compile(r"^resource\s*[\'\"](?P<res_type>\w+)[\'\"]\s*[\'\"](?P<name>\w+)[\'\"]")


def parse_type(line: str) -> str:
    """Parse the resource type"""
    match = RESOURCE_RE.match(line)
    return match.group("res_type") if match else None


def register_parsing_rule(*resources: Type[Resource]) -> Callable[[ParsingRule], ParsingRule]:
    """Decorator to associate parsing rules to resources"""
    def decorator(rule: ParsingRule) -> ParsingRule:
        for resource in resources:
            resource.register_parsing_rule(rule)
        return rule

    return decorator


def register_validation_rule(*resources: Type[Resource]) -> Callable[[ValidationRule], ValidationRule]:
    """Decorator to associate validation rules to resources"""
    def decorator(rule: ValidationRule) -> ValidationRule:
        for resource in resources:
            resource.register_validation_rule(rule)
        return rule

    return decorator


# Parsing and validation rules

def get_kv_config(line: str) -> Tuple[str, str]:
    """Tokenize key value from config
    :return: extracted key value pair
    """
    tokens = line.split('=', 1)
    return tokens[0].strip(), tokens[1].strip().strip('"')


@register_parsing_rule(Resource)
def parse_name(line: str) -> Optional[Property]:
    """Parse name of the resource"""
    match = RESOURCE_RE.match(line)
    if match:
        return "name", match.group("name")
    return None


@register_parsing_rule(SignalFlowResource)
def parse_program_text(line: str) -> Optional[Property]:
    """Parses program text"""
    if line.startswith("program_text"):
        return get_kv_config(line)
    return None


@register_validation_rule(SignalFlowResource)
def validate_parentheses(resource: SignalFlowResource) -> Optional[str]:
    """Warn if parentheses in program_text aren't balanced
    :return: warning message
    """
    def count(char):
        if char == "(":
            return 1
        elif char == ")":
            return -1
        return 0

    if sum(map(count, resource.program_text)) != 0:
        return "Warning: unmatched parentheses in program_text"
    return None


@register_parsing_rule(SignalFlowResource)
def parse_max_delay(line: str) -> Optional[Property]:
    """Parse max delay"""
    if line.startswith("max_delay"):
        key, max_delay = get_kv_config(line)
        return key, int(max_delay)
    return None


@register_validation_rule(Detector)
def validate_max_delay(resource: Detector) -> Optional[str]:
    """Warn if value of max_delay may be too small
    :return: warning message
    """
    if resource.max_delay is None:
        return "Warning: we strongly recommend setting max_delay for detectors"
    return None


@register_parsing_rule(Detector)
def parse_detect_label(line: str) -> Optional[Property]:
    """Parse detect label"""
    if line.startswith("detect_label"):
        return get_kv_config(line)
    return None


@register_validation_rule(Detector)
def validate_detect_labels(resource: Detector) -> Optional[str]:
    """Warn if detect labels are not in the program text
    :return: warning message
    """
    for label in resource.detect_labels:
        if label not in resource.program_text:
            return f"Warning: detect_label:'{label}' not in program_text"
    return None


# Terraform syntax cleanup

HEREDOC_RE = re.compile(r"(.*)<<-?(\S+)\s*$")


class Heredoc(Enum):
    START = auto()
    MIDDLE = auto()
    END = auto()
    NO = auto()


def compact_heredoc(lines: List[str]) -> List[str]:
    start_eof = [
        (i, HEREDOC_RE.match(line).group(2))
        for i, line in enumerate(lines)
        if HEREDOC_RE.match(line)
    ]

    def find_end(eof: str, start: int) -> int:
        EOF_REGEX = re.compile(fr"^\s*{eof}\s*$")
        for i, line in enumerate(lines[start + 1:]):
            if EOF_REGEX.match(line):
                return i + start + 1
        raise ValueError(f"Here-doc inputs are not properly delimited. Can't find end delimiter for: {eof}")

    start_end = [(start, find_end(eof, start)) for start, eof in start_eof]

    def heredoc_where(index: int) -> Heredoc:
        for start, end in start_end:
            if start < index < end:
                return Heredoc.MIDDLE
            if index == start:
                return Heredoc.START
            if index == end:
                return Heredoc.END
        return Heredoc.NO

    heredoc_state = [heredoc_where(i) for i in range(len(lines))]

    def compact(compacted: List[str], indexed_line: Tuple[int, str]) -> List[str]:
        index, line = indexed_line
        state = heredoc_state[index]
        if state == Heredoc.NO:
            return compacted + [line]
        if state == Heredoc.START:
            return compacted + [HEREDOC_RE.match(line).group(1)]
        if state == Heredoc.MIDDLE:
            return compacted[:-1] + [compacted[-1] + "\n" + line]
        if state == Heredoc.END:
            return compacted
        raise ValueError(f"Here-doc inputs are not properly delimited")

    return reduce(compact, enumerate(lines), [])


def strip_comments(line: str) -> str:
    """Remove comments from line"""
    if line.startswith("#"):
        return ""
    return line.rsplit("#", 1)[0].strip()


def clean_conf(tf_conf: IO[Any]) -> List[str]:
    """Clean Terraform configurations from syntax-specific artifacts"""
    lines = [strip_comments(line.strip()) for line in tf_conf]
    lines = [line for line in lines if line]
    lines = compact_heredoc(lines)
    return lines


# Main logic

def parse_resources(tf_conf: IO[Any], available_resources: Dict[str, Type[Resource]]) -> List[Resource]:
    """Parse resources out from the configuration"""
    lines = clean_conf(tf_conf)
    types = [parse_type(line) for line in lines]
    starts = [i for i, t in enumerate(types) if t]
    stanzas = [lines[i:j] for i, j in zip(starts, starts[1:] + [None])]
    types = [t for t in types if t]
    make_resource = partial(find_and_make_resource, available_resources)
    resources = [make_resource(t, stanza) for t, stanza in zip(types, stanzas)]
    return resources


def validate_config(tf_conf: IO[Any], available_resources: Dict[str, Type[Resource]]) -> int:
    """Parse and validate resource starting from a terraform configuration
    :side effect: print warnings
    """
    resources = parse_resources(tf_conf, available_resources)
    warnings = [resource.validate() for resource in resources]
    warnings = [w for w in warnings if w]
    for warning in warnings:
        print(warning)
    return len(warnings)


def validate_file(filename: str, available_resources: Dict[str, Type[Resource]]) -> int:
    with open(filename) as tf_conf:
        return validate_config(tf_conf, available_resources)


def list_filenames(directory: str) -> List[str]:
    """List terraform files in a directory"""
    return [
        os.path.join(directory, filename)
        for filename in os.listdir(directory)
        if filename.endswith('.tf') and filename != 'shared.tf'
    ]


def validate_signalform(args):
    filenames = args.filenames if args.filenames else list_filenames(args.dir)
    retvalue = sum(validate_file(filename, AVAILABLE_RESOURCES) for filename in filenames)
    exit(retvalue)
