import React, { useEffect, useState } from 'react';
import { MakeRequest } from './RequestService';

const GetTask = () => {
  const [problems, setProblems] = useState([]);

  useEffect(() => {
    async function handleProblems() {
      let response = await MakeRequest('http://localhost:5000//contest/${id}', {})
      console.log(response)
      setProblems(response.data.problems)
    }
    handleProblems();
  }, []);

  return (
    <div>
      {problems.map((problem) => (
        <div key={problem.id}>
          <h2>{problem.id}</h2>
          <pre>{JSON.stringify(problem.properties, null, 2)}</pre>
        </div>
      ))}
    </div>
  );
};

export default GetTask;
