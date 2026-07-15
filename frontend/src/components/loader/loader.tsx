import './styles.css';

interface LoaderProps {
  visible: boolean;
  text?: string;
}

function Loader({ visible, text = 'Loading...' }: LoaderProps) {
  if (!visible) return null;

  return (
    <div className="loader-overlay">
      <div className="loader">
        <div className="loader__spinner" />
        <p className="loader__text">{text}</p>
      </div>
    </div>
  );
}

export default Loader;
