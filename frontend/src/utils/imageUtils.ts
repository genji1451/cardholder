// Утилита для получения URL изображения карточки
export const getCardImageUrl = (_seriesNumber: number, cardNumber: number): string => {
  // Определяем серию по номеру карточки:
  // Первая серия (1-275): https://www.laststicker.ru/i/cards/38/[номер].jpg
  // Вторая серия (276-550): https://www.laststicker.ru/i/cards/106/[номер].jpg
  // Третья серия (551-825): https://www.laststicker.ru/i/cards/38/[номер].jpg
  
  if (cardNumber >= 1 && cardNumber <= 275) {
    // Первая серия
    return `https://www.laststicker.ru/i/cards/38/${cardNumber}.jpg`;
  } else if (cardNumber >= 276 && cardNumber <= 550) {
    // Вторая серия
    return `https://www.laststicker.ru/i/cards/106/${cardNumber}.jpg`;
  } else if (cardNumber >= 551 && cardNumber <= 825) {
    // Третья серия
    return `https://www.laststicker.ru/i/cards/166/${cardNumber}.jpg`;
  } else {
    // По умолчанию - первая серия
    return `https://www.laststicker.ru/i/cards/38/${cardNumber}.jpg`;
  }
};

// Утилита для получения URL изображения из данных карточки
export const getCardImageFromData = (card: any): string => {
  if (card.series && card.number) {
    return getCardImageUrl(card.series, card.number);
  }
  return '/images/spiderman/card_1_1.svg'; // Заглушка по умолчанию
};
