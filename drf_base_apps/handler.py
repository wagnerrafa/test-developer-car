"""
Custom logging handlers for the application.

This module provides custom logging handlers that extend the standard Python logging
functionality to provide more specific control over log output and formatting.
"""

import logging


class LevelSpecificFileHandler(logging.FileHandler):
    """
    Manipulador de log que direciona mensagens para um arquivo se o nível do registro for igual ao nível especificado.

    :param filename: O nome do arquivo de log.
    :param custom_level: O nível de log a ser considerado para direcionar mensagens para o arquivo.
    """

    def __init__(self, filename, custom_level):
        """
        Inicializa uma nova instância de LevelSpecificFileHandler.

        :param filename: O nome do arquivo de log.
        :param custom_level: O nível de log a ser considerado para direcionar mensagens para o arquivo.
        """
        super().__init__(filename)
        self.level = custom_level

    def emit(self, record):
        """
        Registra uma mensagem no arquivo de log se o nível do registro for igual ao nível especificado.

        :param record: O registro de log a ser processado.
        """
        if record.levelno == self.level:
            # Chama o método padrão para registrar a mensagem no arquivo
            super().emit(record)
            # Agora, captura o traceback
            if record.exc_info:
                self.format(record)  # Formata o registro novamente, adicionando o traceback
                if self.stream is not None:
                    self.stream.write("".join(self.format(record)))
