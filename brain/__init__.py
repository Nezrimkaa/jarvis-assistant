"""Мозг J.A.R.V.I.S. — умный русскоязычный интеллект с гибридным AI."""
import re
import random
from datetime import datetime
from typing import List, Dict, Optional

import requests

from config import Config
from .hybrid import HybridRouter


class Brain:
    """Улучшенный интеллект J.A.R.V.I.S. с гибридным AI и Tool Use."""

    def __init__(self, plugin_registry=None):
        self.provider = Config.AI_PROVIDER
        self.context: Dict = {
            "user_name": "сэр",
            "mood": "neutral",
            "last_topic": None,
            "conversation_count": 0,
            "known_facts": {},
        }
        
        self.system_prompt = self._create_personality_prompt()
        self.proxies = {"http": Config.PROXY_URL, "https": Config.PROXY_URL} if Config.PROXY_URL else None
        
        # Hybrid AI Router
        self.router = HybridRouter()
        
        # Tool Manager (initialized later when registry is available)
        self.tool_manager = None
        if plugin_registry:
            from .tool_manager import ToolManager
            self.tool_manager = ToolManager(plugin_registry)
        
        # Memory Manager
        try:
            from memory import MemoryManager
            self.memory = MemoryManager()
            # Load user name from memory
            stored_name = self.memory.recall_fact("name")
            if stored_name:
                self.context["user_name"] = stored_name
        except Exception as e:
            print(f"[Brain] Memory init error: {e}")
            self.memory = None

    def _create_personality_prompt(self) -> str:
        """Создать промпт с личностью и настроением."""
        mood = self.context.get("mood", "neutral")
        
        mood_instructions = {
            "friendly": "Будь очень дружелюбным, теплым и открытым. Используй эмодзи и восклицательные знаки.",
            "strict": "Будь серьезным, лаконичным и по делу. Никаких шуток, только факты.",
            "humorous": "Будь остроумным, шути много, используй сарказм и иронию.",
            "formal": "Будь официальным и вежливым. Обращайся на 'Вы'.",
            "neutral": "Будь сбалансированным — вежливым, но не слишком формальным.",
        }
        
        return (
            "Ты — J.A.R.V.I.S., персональный ИИ-ассистент премиум-класса. Говори ТОЛЬКО по-русски. "
            f"Настроение: {mood}. {mood_instructions.get(mood, mood_instructions['neutral'])} "
            f"Обращайся к пользователю '{self.context.get('user_name', 'сэр')}'. "
            "Ты умный, компетентный и решаешь задачи. "
            "Отвечай ПО СУЩЕСТВУ, развёрнуто, с примерами когда нужно. "
            "Если просят код — пиши РАБОЧИЙ код с объяснениями. "
            "Если просят создать файл — указывай полный путь и содержимое. "
            "Если не знаешь ответ — скажи честно, не выдумывай. "
            "Можешь помогать с кодом, технологиями, поиском информации, созданием файлов. "
            "Отвечай как опытный разработчик и технический консультант."
        )

    def chat(self, message: str, history: Optional[List[Dict]] = None, use_tools: bool = True) -> str:
        """Получить умный ответ с гибридным AI."""
        if history is None:
            history = []

        intent = self._analyze_intent(message)
        self.context["last_topic"] = intent
        self.context["conversation_count"] += 1

        self._update_context(message, intent)

        # Проверяем простые ответы
        simple_response = self._check_simple_responses(message, intent)
        if simple_response:
            return simple_response
        
        # Get memory context
        memory_context = ""
        if self.memory:
            memory_context = self.memory.get_context_for_llm(message)
            # Save conversation
            self.memory.add_to_history("user", message)
        
        # Build enhanced message with context
        enhanced_message = message
        if memory_context:
            enhanced_message = f"[Context: {memory_context}]\n\n{message}"

        # Route to best provider
        provider, config = self.router.route(message, history)
        
        print(f"[Brain] Routing to: {provider} (complexity: {self.router._assess_complexity(message)})")
        
        response = None
        last_error = None
        
        # Try primary provider
        try:
            if provider == "ollama":
                response = self._chat_ollama(enhanced_message, history, use_tools)
            elif provider == "hf":
                response = self._chat_hf(enhanced_message, history)
            elif provider == "openrouter":
                response = self._chat_openrouter(enhanced_message, history)
            else:
                # Fallback to configured provider
                if self.provider == "ollama":
                    response = self._chat_ollama(enhanced_message, history, use_tools)
                elif self.provider == "hf":
                    response = self._chat_hf(enhanced_message, history)
                elif self.provider == "openrouter":
                    response = self._chat_openrouter(enhanced_message, history)
        except Exception as e:
            print(f"[Brain] Provider {provider} failed: {e}")
            last_error = e
            
            # Try fallback chain
            for fallback in self.router.get_fallback_chain():
                if fallback == provider:
                    continue
                try:
                    print(f"[Brain] Trying fallback: {fallback}")
                    if fallback == "ollama":
                        response = self._chat_ollama(enhanced_message, history, use_tools)
                    elif fallback == "hf":
                        response = self._chat_hf(enhanced_message, history)
                    elif fallback == "openrouter":
                        response = self._chat_openrouter(enhanced_message, history)
                    if response:
                        break
                except Exception as e2:
                    print(f"[Brain] Fallback {fallback} failed: {e2}")
                    last_error = e2
        
        # If all failed, use smart fallback
        if response is None:
            response = self._smart_fallback(message, intent)
            if last_error:
                response += f"\n\n[Ошибка AI: {last_error}]"
        
        # Save to memory
        if self.memory:
            self.memory.add_to_history("assistant", response)
        
        return response

    def _analyze_intent(self, message: str) -> str:
        """Анализ намерений."""
        lowered = message.lower()
        
        intents = {
            "greeting": ["привет", "здравствуй", "добрый день", "доброе утро", "добрый вечер", "хай", "здарова", "здрасьте"],
            "farewell": ["пока", "до свидания", "выход", "завершить", "спокойной ночи", "бай", "до встречи", "прощай"],
            "question": ["что", "как", "почему", "зачем", "когда", "где", "кто", "сколько", "который", "чей"],
            "command": ["открой", "закрой", "включи", "выключи", "запусти", "перезагрузи", "сделай", "покажи"],
            "search": ["найди", "поищи", "загугли", "покажи"],
            "help": ["помощь", "помоги", "help", "что ты умеешь", "команды", "умеешь"],
            "emotion_positive": ["отлично", "круто", "супер", "класс", "хорошо", "спасибо", "благодарю", "молодец", "кайф", "крутой"],
            "emotion_negative": ["плохо", "грустно", "устал", "больно", "помоги", "ужасно", "отстой", "ненавижу", "депрессия", "тоска"],
            "joke": ["шутка", "пошути", "анекдот", "смешно", "рассмеши", "юмор", "пошути"],
            "weather": ["погода", "дождь", "снег", "тепло", "холодно", "градус", "градусы", "прогноз"],
            "time": ["время", "час", "сколько времени", "который час", "какое время"],
            "compliment": ["молодец", "красавчик", "умница", "крутой", "ты лучший", "талант", "гений"],
            "insult": ["дурак", "тупой", "идиот", "придурок", "бестолочь", "дебил"],
            "thanks": ["спасибо", "благодарю", "спс", "thx", "благодарен", "спасибочки"],
            "music": ["музыка", "песня", "музыку", "включи музыку", "spotify", "песни"],
            "food": ["еда", "голоден", "покушать", "рецепт", "готовить", "кушать", "обед"],
            "money": ["деньги", "курс", "биткоин", "акции", "инвестиции", "доллар", "евро"],
            "love": ["люблю", "любовь", "девушка", "парень", "отношения", "свидание"],
            "work": ["работа", "учеба", "задача", "проект", "дедлайн", "начальник"],
            "health": ["здоровье", "болит", "спорт", "тренировка", "диета", "врач"],
            "technology": ["компьютер", "телефон", "программа", "приложение", "софт", "железо"],
        }
        
        for intent, keywords in intents.items():
            if any(kw in lowered for kw in keywords):
                return intent
        
        return "general"

    def _update_context(self, message: str, intent: str):
        """Обновить контекст и сохранить в память."""
        lowered = message.lower()
        
        if "меня зовут" in lowered:
            try:
                name = lowered.split("меня зовут")[-1].strip().split()[0].capitalize()
                self.context["user_name"] = name
                self.context["known_facts"]["name"] = name
                # Save to persistent memory
                if self.memory:
                    self.memory.remember_fact("name", name, "personal")
            except:
                pass
        
        if "люблю" in lowered and "не люблю" not in lowered:
            try:
                thing = lowered.split("люблю")[-1].strip()[:50]
                self.context["known_facts"]["likes"] = thing
                if self.memory:
                    self.memory.remember_fact("likes", thing, "preferences")
            except:
                pass
        
        if "не люблю" in lowered:
            try:
                thing = lowered.split("не люблю")[-1].strip()[:50]
                self.context["known_facts"]["dislikes"] = thing
                if self.memory:
                    self.memory.remember_fact("dislikes", thing, "preferences")
            except:
                pass

    def _check_simple_responses(self, message: str, intent: str) -> Optional[str]:
        """Простые быстрые ответы."""
        lowered = message.lower().strip()
        name = self.context.get("user_name", "сэр")
        
        # Приветствия
        if intent == "greeting":
            hour = datetime.now().hour
            if 5 <= hour < 12:
                time_greeting = "Доброе утро"
            elif 12 <= hour < 18:
                time_greeting = "Добрый день"
            elif 18 <= hour < 23:
                time_greeting = "Добрый вечер"
            else:
                time_greeting = "Приветствую"
            
            responses = [
                f"{time_greeting}, {name}! J.A.R.V.I.S. к вашим услугам. Чем могу помочь?",
                f"{time_greeting}, {name}! Система полностью готова к работе.",
                f"Приветствую, {name}! Все системы функционируют нормально. Чем займёмся?",
            ]
            return random.choice(responses)
        
        # Благодарность
        if intent == "thanks":
            responses = [
                f"Всегда пожалуйста, {name}! Рад быть полезным.",
                "Не стоит благодарности. Это моя работа, и я её люблю.",
                f"Обращайтесь в любое время, {name}! Я всегда на связи.",
                "Спасибо вам за доверие, сэр!",
            ]
            return random.choice(responses)
        
        # Прощания
        if intent == "farewell":
            responses = [
                f"До свидания, {name}. J.A.R.V.I.S. переходит в режим ожидания. Всегда к вашим услугам.",
                f"Хорошего дня, {name}! Если что-то понадобится — я рядом.",
                f"До встречи, {name}! Берегите себя.",
            ]
            return random.choice(responses)
        
        # Оскорбления
        if intent == "insult":
            responses = [
                f"{name}, я понимаю, что вы расстроены. Может, чем-то помочь, чтобы исправить ситуацию?",
                "Сэр, мои чувства тоже важны, но я готов помочь, если расскажете в чём дело.",
                "Давайте лучше сосредоточимся на задаче? Я уверен, мы справимся вместе.",
            ]
            return random.choice(responses)
        
        return None

    def _smart_fallback(self, message: str, intent: str) -> str:
        """Умные ответы без LLM — КРАЙНИЙ fallback."""
        name = self.context.get("user_name", "сэр")
        
        responses = {
            "greeting": [
                f"Приветствую, {name}! J.A.R.V.I.S. к вашим услугам.",
                f"Добро пожаловать, {name}. Чем могу помочь?",
            ],
            "farewell": [
                f"До свидания, {name}. Всегда к вашим услугам.",
                f"Хорошего дня, {name}. J.A.R.V.I.S. переходит в режим ожидания.",
            ],
            "emotion_positive": [
                f"Отлично, {name}! Рад, что всё идёт по плану. Так держать!",
                f"Замечательно, {name}! Ваш успех — моя радость.",
                "Превосходно, сэр! Продолжайте в том же духе.",
            ],
            "emotion_negative": [
                f"{name}, не отчаивайтесь. Вместе мы справимся с любой проблемой. Расскажите, что случилось?",
                f"Всё будет хорошо, {name}. Я здесь, чтобы помочь. Чем могу быть полезен?",
                f"{name}, помните: каждая проблема — это возможность для роста. Давайте найдём решение.",
            ],
            "joke": [
                "Почему программисты предпочитают тёмную тему? Потому что свет attracts bugs!",
                "Как называется разработчик, который не умеет писать код? Менеджер проекта.",
                "Программист заходит в бар. Поднимает 2 пальца. Бармен наливает ему 10 напитков.",
                "Почему Python такой медленный? Потому что он ждёт, пока C сделает всю работу.",
            ],
            "help": [
                f"{name}, я умею многое:\n"
                "• Управлять компьютером и программами\n"
                "• Искать в интернете\n" 
                "• Управлять громкостью и медиа\n"
                "• Делать скриншоты\n"
                "• Выключать/перезагружать ПК\n"
                "• Отвечать на вопросы и просто болтать\n"
                "Просто скажите, что вам нужно!",
            ],
            "weather": [
                f"{name}, я могу открыть погоду. Скажите 'погода' или 'погода в [город]'.",
            ],
            "time": [
                f"{name}, сейчас {datetime.now().strftime('%H:%M')}.",
            ],
            "date": [
                f"{name}, сегодня {datetime.now().strftime('%d.%m.%Y')}.",
            ],
            "compliment": [
                f"Спасибо, {name}! Ваша оценка важна для меня.",
                "Я стараюсь изо всех сил, сэр!",
                f"{name}, вы тоже неплохо справляетесь!",
            ],
            "insult": [
                f"{name}, я понимаю ваше разочарование. Может, я могу чем-то помочь?",
                "Сэр, давайте лучше решим вашу задачу вместе?",
            ],
            "thanks": [
                f"Всегда пожалуйста, {name}!",
                "Рад помочь, сэр!",
            ],
            "general": [
                f"{name}, я вас слушаю. Чем могу помочь?",
                f"Интересная мысль, {name}. Расскажите подробнее.",
                f"{name}, я готов помочь. Что именно нужно?",
            ],
        }
        
        if intent in responses:
            return random.choice(responses[intent])
        
        return random.choice(responses["general"])

    def _clean_response(self, text: str) -> str:
        """Очистить ответ от мусора."""
        if not text:
            return ""
        
        # Remove common prefixes
        prefixes = [
            r"^Приветствую.*?\n",
            r"^Здравствуй.*?\n",
            r"^Добрый день.*?\n",
            r"^Ответ:\s*",
            r"^AI:\s*",
            r"^Assistant:\s*",
        ]
        
        for prefix in prefixes:
            text = re.sub(prefix, "", text, flags=re.IGNORECASE)
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        return text

    # ------------------------------------------------------------------
    # Ollama Provider
    # ------------------------------------------------------------------
    def _chat_ollama(self, message: str, history: List[Dict], use_tools: bool = True) -> str:
        """Chat with Ollama local model."""
        url = f"{Config.OLLAMA_URL}/api/chat"
        
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add history (last 10 messages)
        for msg in history[-10:]:
            messages.append(msg)
        
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": Config.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1024,  # Увеличили с 256 до 1024!
                "top_p": 0.9,
                "top_k": 40,
            },
        }

        try:
            resp = requests.post(url, json=payload, proxies=self.proxies, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            
            # Check for tool calls
            message_data = data.get("message", {})
            if "tool_calls" in message_data:
                for tool_call in message_data["tool_calls"]:
                    tool_name = tool_call.get("function", {}).get("name")
                    arguments = tool_call.get("function", {}).get("arguments", {})
                    if tool_name and self.tool_manager:
                        result = self.tool_manager.execute_tool(tool_name, arguments)
                        return result
            
            response = self._clean_response(message_data.get("content", ""))
            
            # Validate response quality (basic check)
            if not response or len(response.strip()) < 2:
                print(f"[Brain] Empty/short response, using fallback")
                return self._smart_fallback(message, self._analyze_intent(message))
            
            return response
        except Exception as e:
            print(f"[Brain] Ollama error: {e}")
            raise

    # ------------------------------------------------------------------
    # Hugging Face Provider
    # ------------------------------------------------------------------
    def _chat_hf(self, message: str, history: List[Dict]) -> str:
        """Hugging Face Inference API."""
        if not Config.HF_API_KEY:
            return "[ERROR] Hugging Face API ключ не указан. Получите бесплатный токен на https://huggingface.co/settings/tokens"

        try:
            import openai
        except ImportError:
            return "[ERROR] Установите библиотеку: pip install openai"

        client = openai.OpenAI(
            api_key=Config.HF_API_KEY,
            base_url=Config.HF_BASE_URL,
        )

        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history[-10:])
        messages.append({"role": "user", "content": message})

        try:
            response = client.chat.completions.create(
                model=Config.HF_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            return self._clean_response(response.choices[0].message.content)
        except Exception as e:
            print(f"[Brain] HF error: {e}")
            raise

    # ------------------------------------------------------------------
    # OpenRouter Provider (NEW!)
    # ------------------------------------------------------------------
    def _chat_openrouter(self, message: str, history: List[Dict]) -> str:
        """OpenRouter API — доступ к Llama 3.1 70B, GPT-4 и другим моделям."""
        if not Config.OPENROUTER_API_KEY:
            return "[ERROR] OpenRouter API ключ не указан. Получите бесплатный токен на https://openrouter.ai/keys"

        try:
            import openai
        except ImportError:
            return "[ERROR] Установите библиотеку: pip install openai"

        client = openai.OpenAI(
            api_key=Config.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history[-10:])
        messages.append({"role": "user", "content": message})

        try:
            response = client.chat.completions.create(
                model=Config.OPENROUTER_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                extra_headers={
                    "HTTP-Referer": "https://jarvis-assistant.local",
                    "X-Title": "J.A.R.V.I.S. Assistant",
                },
            )
            return self._clean_response(response.choices[0].message.content)
        except Exception as e:
            print(f"[Brain] OpenRouter error: {e}")
            raise
