export interface Series {
  id: number;
  number: number;
  title: string;
}

export interface Tag {
  id: number;
  name: string;
}

export interface Card {
  id: number;
  title: string;
  number: number;
  rarity: 'o' | 'ск' | 'ук';
  series: number;
  series_title: string;
  base_price_rub: number;
  notes: string;
  tags: Tag[];
}

export interface InventoryItem {
  id: number;
  card: Card;
  card_id: number;
  has_card: boolean;
  quantity: number;
  condition: 'M' | 'NM' | 'SP' | 'MP' | 'HP' | 'DM' | 'NO';
  user_rating?: number;
  note: string;
  images: CardImage[];
}

export interface CardImage {
  id: number;
  image: string;
  created_at: string;
}

export interface Trade {
  id: number;
  card: Card;
  card_id: number;
  trade_type: 'buy' | 'sell';
  quantity: number;
  price_rub: number;
  fees_rub: number;
  date: string;
  note: string;
}

export interface PriceRecord {
  id: number;
  card: Card;
  card_id: number;
  source: string;
  price_rub: number;
  recorded_at: string;
}

export interface WishlistItem {
  id: number;
  card: Card;
  card_id: number;
  priority: 1 | 2 | 3;
  target_price_rub?: number;
  note: string;
  created_at: string;
}

export interface AnalyticsOverview {
  total_cards: number;
  owned_cards: number;
  completion_percentage: number;
  total_value: number;
  recent_trades: {
    card_title: string;
    quantity: number;
    price: number;
    date: string;
  }[];
}

export interface AnalyticsDistribution {
  rarity: {
    card__rarity: string;
    count: number;
  }[];
  series: {
    card__series__number: number;
    card__series__title: string;
    count: number;
  }[];
}

export interface SeriesProgress {
  series_id: number;
  series_title: string;
  series_number: number;
  total: number;
  owned: number;
  percentage: number;
}

export interface AnalyticsProgress {
  series_progress: SeriesProgress[];
}

export interface ValueTrendPoint {
  month: string;
  total_spent: number;
  avg_price: number;
}

export interface AnalyticsValueTrend {
  value_trend: ValueTrendPoint[];
}
