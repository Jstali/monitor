import React, { useState, useEffect } from 'react';
import { Image as ImageIcon } from 'lucide-react';
import api from '../services/api';

const AuthenticatedImage = ({ url, alt, className, onClick }) => {
  const [imageSrc, setImageSrc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let isMounted = true;
    
    const fetchImage = async () => {
      try {
        setLoading(true);
        const response = await api.get(url, { responseType: 'blob' });
        
        if (isMounted) {
          const objectUrl = URL.createObjectURL(response.data);
          setImageSrc(objectUrl);
          setLoading(false);
        }
      } catch (err) {
        console.error('Failed to load image:', err);
        if (isMounted) {
          setError(true);
          setLoading(false);
        }
      }
    };

    if (url) {
      fetchImage();
    }

    return () => {
      isMounted = false;
      if (imageSrc) {
        URL.revokeObjectURL(imageSrc);
      }
    };
  }, [url]);

  if (loading) {
    return (
      <div className={`image-placeholder ${className}`} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f3f4f6' }}>
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`image-placeholder ${className}`} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fee2e2', color: '#ef4444' }}>
        <ImageIcon size={24} />
      </div>
    );
  }

  return (
    <img 
      src={imageSrc} 
      alt={alt} 
      className={className} 
      onClick={onClick}
    />
  );
};

export default AuthenticatedImage;
