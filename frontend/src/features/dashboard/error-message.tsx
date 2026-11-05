import { ApiError } from '../../api/client';

function fieldMessages(error: Error): string[] {
  if (!(error instanceof ApiError)) return [];
  return Object.entries(error.errors).flatMap(([field, messages]) =>
    messages.map((message) => (message.startsWith(field) ? message : `${field}: ${message}`)),
  );
}

interface ErrorMessageProps {
  error: Error;
}

export function ErrorMessage({ error }: ErrorMessageProps) {
  const details = fieldMessages(error);
  return (
    <div role='alert' className='text-sm text-red-700'>
      <p>{error.message}</p>
      {details.length > 0 && (
        <ul className='list-disc pl-5'>
          {details.map((detail) => (
            <li key={detail}>{detail}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
