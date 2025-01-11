class LLMException(Exception):
    """Exceção para erros relacionados ao processamento de linguagem natural"""
    pass

class ValidationError(Exception):
    """Exceção para erros de validação de dados"""
    pass

class ServiceUnavailable(Exception):
    """Exceção para serviços indisponíveis"""
    pass