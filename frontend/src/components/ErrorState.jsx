import './ErrorState.css';

export default function ErrorState({
  title = 'Something went wrong',
  message = 'Unable to load data.',
}) {
  return (
    <div className="error-state">
      <h2>{title}</h2>

      <p>{message}</p>
    </div>
  );
}