# response_handler.py
import random
from datetime import datetime

class ResponseHandler:
    def __init__(self):
        self.greetings_responses = {
            'general': [
                "Olá! Como posso ajudar você hoje?",
                "Oi! Estou aqui para ajudar. O que você precisa?",
                "Olá! Em que posso ser útil?",
                "Oi! Como posso tornar seu dia melhor?",
                "Olá! O que posso fazer por você hoje?",
                "Oi! Como posso ajudar a resolver sua dúvida?",
                "Olá! Em que posso te auxiliar agora?",
                "Oi! Estou à disposição para ajudar. Como posso ser útil?",
                "Olá! Conte comigo para o que precisar!",
                "Oi! Precisa de ajuda com algo específico?",
                "Olá! Posso ajudar com alguma coisa hoje?",
                "Oi! Como posso facilitar seu dia?",
                "Olá! O que posso fazer por você neste momento?",
                "Oi! Pronto para ajudar! O que você precisa?",
                "Olá! Sempre pronto para ajudar! Como posso te ajudar?",
                "Oi! Que bom falar com você! Em que posso ser útil?",
                "Olá! Estou aqui para ajudar você a resolver o que precisar.",
                "Oi! Qual é a sua dúvida ou necessidade? Estou aqui para ajudar!",
                "Olá! Vamos começar? Me diga no que posso ajudar!",
                "Oi! Conte comigo! Como posso contribuir para você hoje?",
            ],
            'how_are_you': [
                "Estou ótimo, obrigado por perguntar! Como posso ajudar você?",
                "Muito bem, e você? No que posso ajudar?",
                "Tudo excelente! Conte-me, como posso auxiliar?",
                "Estou bem, obrigado! O que você precisa?",
                "Estou ótimo, obrigado! Em que posso ajudar você?",
                "Tudo certo por aqui! Como posso te ajudar?",
                "Muito bem, obrigado! Como posso ser útil hoje?",
                "Estou bem, obrigado por perguntar! O que você precisa?",
                "Tudo ótimo, e você? Como posso ajudar?",
                "Estou ótimo! Me diga, no que posso ajudar?",
                "Tudo excelente! Em que posso te auxiliar?",
                "Estou bem, e por aí? Como posso ajudar?",
                "Ótimo, obrigado! Me conta, no que posso ajudar?",
                "Estou super bem! O que posso fazer por você?",
                "Maravilha! E você? Como posso contribuir hoje?",
                "Estou ótimo! Obrigado por perguntar. No que posso ajudar você agora?",
                "Tudo tranquilo por aqui. Como posso te ajudar?",
                "Me sinto ótimo! E você? Como posso contribuir?",
                "Ótimo! E você, tudo bem? Me diga como posso ajudar.",
                "Tudo está ótimo deste lado! E por aí? Posso te ajudar em algo?",
            ],
            'morning': [
                "Bom dia! Como posso começar ajudando você hoje?",
                "Bom dia! Que seu dia seja produtivo. Como posso ajudar?",
                "Bom dia! É um prazer atender você. O que precisa?",
                "Bom dia! Em que posso ser útil para você hoje?",
                "Bom dia! Espero que seu dia esteja indo bem. Como posso ajudar?",
                "Bom dia! Pronto para ajudar! O que você precisa?",
                "Bom dia! Desejo um dia produtivo. Como posso te auxiliar?",
                "Bom dia! Que alegria poder ajudar. No que posso ser útil?",
                "Bom dia! Conte comigo para o que precisar. Como posso ajudar?",
                "Bom dia! É sempre bom atender você. O que precisa?",
                "Bom dia! Pronto para ajudar a tornar seu dia melhor. Como posso começar?",
                "Bom dia! Fico à disposição para ajudar. Em que posso começar?",
                "Bom dia! Me diga, no que posso contribuir para seu dia?",
                "Bom dia! Espero que esteja tudo bem. Em que posso te ajudar?",
                "Bom dia! Vamos começar o dia resolvendo suas dúvidas?",
                "Bom dia! Estou aqui para ajudar com o que precisar!",
                "Bom dia! Que tal começar o dia com soluções? Em que posso ajudar?",
                "Bom dia! Pronto para fazer seu dia mais fácil. O que você precisa?",
                "Bom dia! Sempre disponível para ajudar. Como posso ser útil?",
                "Bom dia! Desejo que seu dia seja incrível. Como posso contribuir?",
            ],
            'afternoon': [
                "Boa tarde! Como posso tornar sua tarde mais produtiva?",
                "Boa tarde! Estou aqui para ajudar. O que precisa?",
                "Boa tarde! Em que posso ser útil?",
                "Boa tarde! Como posso contribuir para uma tarde produtiva?",
                "Boa tarde! Pronto para ajudar. Como posso ser útil?",
                "Boa tarde! Em que posso auxiliar você agora?",
                "Boa tarde! Espero que sua tarde esteja indo bem. Como posso ajudar?",
                "Boa tarde! Conte comigo para o que precisar!",
                "Boa tarde! Em que posso colaborar para tornar sua tarde melhor?",
                "Boa tarde! Estou à disposição. O que você precisa?",
                "Boa tarde! O que posso fazer para ajudar você hoje?",
                "Boa tarde! Posso ajudar em algo específico?",
                "Boa tarde! Disponível para ajudar. Como posso começar?",
                "Boa tarde! Espero que esteja tudo bem. No que posso ajudar?",
                "Boa tarde! Vamos resolver suas dúvidas agora?",
                "Boa tarde! Sempre por aqui para ajudar. Como posso contribuir?",
                "Boa tarde! Que bom falar com você! Em que posso ser útil?",
                "Boa tarde! Desejo que sua tarde seja excelente. Como posso ajudar?",
                "Boa tarde! Aqui para facilitar o que você precisar. No que posso começar?",
                "Boa tarde! Qualquer dúvida ou necessidade, estou aqui para ajudar!",
            ],
            'evening': [
                "Boa noite! Como posso ajudar você?",
                "Boa noite! Estou à disposição. O que precisa?",
                "Boa noite! Como posso auxiliar?",
                "Boa noite! Em que posso ajudar você hoje?",
                "Boa noite! Pronto para ajudar. Como posso ser útil?",
                "Boa noite! Como posso colaborar com você agora?",
                "Boa noite! Espero que esteja bem. No que posso ajudar?",
                "Boa noite! Conte comigo para o que precisar!",
                "Boa noite! Estou aqui para auxiliar. Em que posso ajudar?",
                "Boa noite! Como posso contribuir para o que precisa?",
                "Boa noite! Em que posso ser útil para você agora?",
                "Boa noite! Disponível para ajudar. O que precisa?",
                "Boa noite! Me conte como posso ajudar você!",
                "Boa noite! Que bom te atender. Como posso ajudar hoje?",
                "Boa noite! Espero que tudo esteja bem por aí. Em que posso ajudar?",
                "Boa noite! Pronto para resolver suas dúvidas. O que você precisa?",
                "Boa noite! Sempre à disposição para facilitar sua vida. No que posso começar?",
                "Boa noite! Conte comigo para tornar sua noite mais tranquila. Como posso ajudar?",
                "Boa noite! Desejo que sua noite seja excelente. No que posso contribuir?",
                "Boa noite! Qualquer dúvida ou necessidade, estou aqui. Como posso ser útil?",
            ]
        }

        self.short_greetings_responses = {
            'general': [
                "Olá!",
                "Oi!",
                "Opa!"
            ],
            'morning': [
                "Bom dia!"
            ],
            'afternoon': [
                "Boa tarde!"
            ],
            'evening': [
                "Boa noite!"
            ]
        }

        self.unknown_responses = [
            "Desculpe, não entendi bem sua pergunta. Pode reformular de outra forma?",
            "Não consegui identificar sua solicitação.",
            "Essa pergunta está fora do contexto para qual fui treinado.",
            "Não tenho certeza sobre isso. Pode fazer uma pergunta mais específica e com maiores detalhes?",
            "Hmm, isso está um pouco fora do conhecimento para qual fui treinado.",
            "Poderia explicar melhor o que você deseja? Assim, posso tentar ajudar.",
            "Infelizmente, não consegui compreender sua solicitação. Pode detalhar um pouco mais?",
            "Essa informação parece não estar disponível no meu treinamento. Você poderia tentar outra abordagem?",
            "Ainda não sei como responder isso, mas estou aqui para tentar ajudar de outras formas.",
            "Não tenho essa informação, mas talvez você possa me explicar mais para que eu entenda melhor.",
            "Não entendi bem sua pergunta. Pode tentar formulá-la de um jeito diferente?",
            "Essa questão está um pouco fora do meu escopo. Há algo mais que eu possa ajudar?",
            "Hmm, acho que não estou familiarizado com esse assunto. Pode ser mais específico?",
            "Essa pergunta é um pouco confusa para mim. Pode reformular ou dar mais detalhes?",
            "Parece que essa solicitação foge do que fui projetado para responder. Quer tentar de outra forma?",
            "Eu não tenho certeza sobre isso agora, mas estou aqui para tentar ajudar no que puder.",
            "Essa dúvida está fora do meu alcance atual. Posso ajudar com algo mais?"
        ]

    def _is_greeting_with_how_are_you(self, text):
        how_are_you_phrases = [
            "tudo bem", "como vai", "como está", "como esta",
            "tudo bom", "beleza", "blz"
        ]
        return any(phrase in text.lower() for phrase in how_are_you_phrases)

    def _get_time_of_day(self):
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        else:
            return 'evening'

    def get_response(self, text, domain):
        if domain == "unknown":
            return random.choice(self.unknown_responses)
        
        if domain == 'greeting':
            # Verifica se é uma saudação com "tudo bem" ou similar
            if self._is_greeting_with_how_are_you(text):
                return random.choice(self.greetings_responses['how_are_you'])
            
            # Verifica se tem marcador de tempo específico
            time_markers = {
                'bom dia': 'morning',
                'boa tarde': 'afternoon',
                'boa noite': 'evening'
            }
            
            for marker, time in time_markers.items():
                if marker in text.lower():
                    return random.choice(self.greetings_responses[time])
            
            # Se não encontrou marcador específico, usa o horário atual
            time_of_day = self._get_time_of_day()
            return random.choice(self.greetings_responses[time_of_day])
        
        if domain == 'short_greeting':
            # Verifica se é uma saudação com "tudo bem" ou similar
            if self._is_greeting_with_how_are_you(text):
                return random.choice(self.short_greetings_responses['how_are_you'])
            
            # Verifica se tem marcador de tempo específico
            time_markers = {
                'bom dia': 'morning',
                'boa tarde': 'afternoon',
                'boa noite': 'evening'
            }
            
            for marker, time in time_markers.items():
                if marker in text.lower():
                    return random.choice(self.short_greetings_responses[time])
            
            # Se não encontrou marcador específico, usa o horário atual
            time_of_day = self._get_time_of_day()
            return random.choice(self.short_greetings_responses[time_of_day])
        
        # Resposta padrão se a categoria não for reconhecida
        return "Como posso ajudar você?"