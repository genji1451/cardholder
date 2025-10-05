import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../api/client';
import './AddCardModal.css';

interface AddCardModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AddCardModal = ({ isOpen, onClose }: AddCardModalProps) => {
  const [selectedCard, setSelectedCard] = useState<number | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [condition, setCondition] = useState('NM');
  const [price, setPrice] = useState('');
  
  const queryClient = useQueryClient();

  const { data: cards } = useQuery({
    queryKey: ['cards'],
    queryFn: async () => {
      const response = await apiClient.get('/cards/');
      return response.data.results || response.data;
    },
  });

  const addToInventoryMutation = useMutation({
    mutationFn: async (data: any) => {
      return await apiClient.post('/inventory/items/', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
      onClose();
      resetForm();
    },
  });

  const resetForm = () => {
    setSelectedCard(null);
    setQuantity(1);
    setCondition('NM');
    setPrice('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCard) return;

    const card = cards?.find((c: any) => c.id === selectedCard);
    if (!card) return;

    const data = {
      card_id: selectedCard,
      has_card: true,
      quantity: quantity,
      condition: condition,
      user_rating: 4.5,
    };

    addToInventoryMutation.mutate(data);

    // Add trade record if price is provided
    if (price && parseFloat(price) > 0) {
      apiClient.post('/finance/trades/', {
        card_id: selectedCard,
        trade_type: 'buy',
        quantity: quantity,
        price_rub: parseFloat(price),
        fees_rub: 0,
        date: new Date().toISOString().split('T')[0],
        note: 'Added to collection'
      });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Add Card to Collection</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label>Select Card</label>
            <select
              value={selectedCard || ''}
              onChange={(e) => setSelectedCard(parseInt(e.target.value))}
              required
              className="form-select"
            >
              <option value="">Choose a card...</option>
              {cards?.map((card: any) => (
                <option key={card.id} value={card.id}>
                  {card.title} #{card.number} - {card.series_title}
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Quantity</label>
              <input
                type="number"
                min="1"
                value={quantity}
                onChange={(e) => setQuantity(parseInt(e.target.value))}
                className="form-input"
                required
              />
            </div>

            <div className="form-group">
              <label>Condition</label>
              <select
                value={condition}
                onChange={(e) => setCondition(e.target.value)}
                className="form-select"
              >
                <option value="M">Mint</option>
                <option value="NM">Near Mint</option>
                <option value="SP">Slightly Played</option>
                <option value="MP">Moderately Played</option>
                <option value="HP">Heavily Played</option>
                <option value="DM">Damaged</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Purchase Price (optional)</label>
            <input
              type="number"
              step="0.01"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              placeholder="0.00"
              className="form-input"
            />
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn-primary"
              disabled={addToInventoryMutation.isPending}
            >
              {addToInventoryMutation.isPending ? 'Adding...' : 'Add to Collection'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddCardModal;
