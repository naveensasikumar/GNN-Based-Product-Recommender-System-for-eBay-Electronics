import { useState } from 'react';
import { Carousel } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

export default function GNNRecommenderUI() {
  const [itemId, setItemId] = useState('');
  const [viewedItem, setViewedItem] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const [categoryName, setCategoryName] = useState('');
  const [condition, setCondition] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');

  const [clusterItems, setClusterItems] = useState([]);

  const fetchRecommendations = async () => {
    setLoading(true);
    const payload = {
      user_item_id: itemId.trim(),
      top_k: 10,
      category_name: categoryName || undefined,
      condition: condition || undefined,
      min_price: minPrice ? parseFloat(minPrice) : undefined,
      max_price: maxPrice ? parseFloat(maxPrice) : undefined
    };

    const res = await fetch('http://localhost:8000/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    setViewedItem(data.viewed_item || null);
    setRecommendations(data.recommendations || []);
    setLoading(false);
  };


const fetchClusterItems = async () => {
  const res = await fetch(`http://localhost:8000/cluster-items/${itemId}`);
  const data = await res.json();
  setClusterItems(data.items || []);
};


  return (
    <div className="container mt-5">
      <h1 className="mb-4">GNN Recommender System</h1>

      {/* Item ID Input */}
      <div className="mb-4 row">
        <div className="col-md-6">
          <label className="form-label">Enter Item ID:</label>
          <input
            type="text"
            className="form-control"
            value={itemId}
            onChange={(e) => setItemId(e.target.value)}
            placeholder="e.g. v1|123456|0"
          />
        </div>
        <div className="col-md-6 d-flex align-items-end gap-2">
  <button
    className="btn btn-primary w-50"
    onClick={fetchRecommendations}
    disabled={loading || !itemId}
  >
    {loading ? 'Loading...' : 'Get Recommendations'}
  </button>
  <button
    className="btn btn-outline-secondary w-50"
    onClick={fetchClusterItems}
    disabled={!itemId}
  >
    Get Cluster Items
  </button>
</div>
      </div>

      {/* Filters */}
      <div className="row g-3 mb-4">
        <div className="col-md-3">
          <label className="form-label">Category</label>
          <input className="form-control" value={categoryName} onChange={(e) => setCategoryName(e.target.value)} />
        </div>
        <div className="col-md-3">
          <label className="form-label">Condition</label>
          <input className="form-control" value={condition} onChange={(e) => setCondition(e.target.value)} />
        </div>
        <div className="col-md-3">
          <label className="form-label">Min Price</label>
          <input type="number" className="form-control" value={minPrice} onChange={(e) => setMinPrice(e.target.value)} />
        </div>
        <div className="col-md-3">
          <label className="form-label">Max Price</label>
          <input type="number" className="form-control" value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} />
        </div>
      </div>

      {/* Viewed Item */}
      {viewedItem && (
        <div className="card mb-5">
          <div className="card-header fw-bold">Viewed Item</div>
          <div className="card-body d-flex">
            <img src={viewedItem.image} alt={viewedItem.title} style={{ width: '120px', marginRight: '20px' }} />
            <div>
              <h5>{viewedItem.title}</h5>
              <p><strong>Price:</strong> {viewedItem.price?.value} {viewedItem.price?.currency}</p>
              <p><strong>Category:</strong> {viewedItem.category_name}</p>
              <p><strong>Condition:</strong> {viewedItem.condition}</p>
              <p><strong>Seller:</strong> {viewedItem.seller_username}</p>
              <p><strong>Location:</strong> {viewedItem.location}</p>
              <p><strong>Description:</strong> {viewedItem.shortDescription}</p>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <>
          <h4 className="mb-3">Recommended Items</h4>
          <Carousel interval={null}>
            {recommendations.map((rec, i) => (
              <Carousel.Item key={i}>
                <div className="d-flex justify-content-center">
                  <div className="card w-75 p-3">
                    <div className="row g-0">
                      <div className="col-md-4">
                        <img src={rec.image} className="img-fluid" alt={rec.title} />
                      </div>
                      <div className="col-md-8">
                        <div className="card-body">
                          <h5 className="card-title">{rec.title}</h5>
                          <p><strong>Price:</strong> {rec.price?.value} {rec.price?.currency}</p>
                          <p><strong>Condition:</strong> {rec.condition}</p>
                          <p><strong>Category:</strong> {rec.category_name}</p>
                          <p><strong>Seller:</strong> {rec.seller_username}</p>
                          <p><strong>Location:</strong> {rec.location}</p>
                          <p><strong>Description:</strong> {rec.shortDescription}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Carousel.Item>
            ))}
          </Carousel>
        </>
      )}

      {/* Cluster Browse */}
    

      {clusterItems.length > 0 && (
  <>
    <h4 className="mt-5">Items from Same Cluster</h4>
    <Carousel controls indicators interval={null}>
      {clusterItems.map((item, i) => (
        <Carousel.Item key={i}>
          <div className="d-flex justify-content-center">
            <div className="card w-75 p-3">
              <div className="row g-0">
                <div className="col-md-4">
                  <img src={item.image} className="img-fluid" alt={item.title} />
                </div>
                <div className="col-md-8">
                  <div className="card-body">
                    <h5 className="card-title">{item.title}</h5>
                    <p><strong>Price:</strong> {item.price}</p>
                    <p><strong>Condition:</strong> {item.condition}</p>
                    <p><strong>Category:</strong> {item.category_name}</p>
                    <p><strong>Seller:</strong> {item.seller_username}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Carousel.Item>
      ))}
    </Carousel>
  </>
)}

      
    </div>
  );
}
