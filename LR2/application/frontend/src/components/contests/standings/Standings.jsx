import React, { useEffect, useState } from 'react';
import styles from '../TaskResultStyles.module.css';
import tableStyles from './Standings.module.css';
import { useParams } from "react-router-dom";
import { MakeRequest } from '../../../API/RequestService';

const Standings = () => {
  const [data, setData] = useState();
  const [problems, setProblems] = useState();

  const { id } = useParams();

  useEffect(() => {
    async function handleData() {
      let response = await MakeRequest(`contest/${id}/standings`, {})
      setData(response.data.results)

      response = await MakeRequest(`contest/${id}`, {})
      setProblems(response.data.problems)
    }
    handleData();
  }, [id]);

  const getCounterLabel = (index) => {
    const counter = String.fromCharCode(65 + index); // Начинается с буквы A
    return counter;
  };

  function setResults(problems_result) {
    const list = [];
    for (let i = 0; i < problems.length; i++) {
      let res = "";
      for (let j = 0; j < problems_result.length; j++) {
        if (problems_result[j].problem_id === problems[i].id) {
          res = (problems_result[j].result === 1 ? "+" : (problems_result[j].attempts_count > 0 ? "-" : "")) + (problems_result[j].attempts_count > 1 ? problems_result[j].attempts_count - 1 : "");
        }
      }
      list.push(<td key = {i} className={`${styles.Letter} ${tableStyles.td}`}>
        {res}
      </td>);
    }
    return list
  }

  function showStandings() {
    if (!data || data.length == 0 || !problems) {
      return <tr>
                <td colSpan="4">Нет доступных задач.</td>
             </tr>
    }
    const rows = []
    data.sort((itemA, itemB) => itemA.contest_result > itemB.contest_result ? 1 : -1)
    data.map((item, rowIndex) => (
      rows.push(<tr key={item.id}>
        <td>{rowIndex + 1}</td>
        <td>{item.login}</td>
        <td>{item.contest_result}</td>
        <td>{item.penalty}</td>
        {setResults(item.problems_result)}
      </tr>)
    ))
    return rows;
  }
  
  function showCounters() {
    if (!problems) {
      return <></>
    }
    const counters = []
    problems.map((problem, index) => (
      counters.push(<th className={styles.Letter}>
        {getCounterLabel(index)}
      </th>)
    ))
    return counters
  }

  //{"results":[{"login":"kartel","contest_result":2,"penalty":87,"problems_result":[{"result":1,"attempts_count":3,"last_attempt":{"Time":"2023-04-19T19:48:34+03:00","Valid":true}},{"result":1,"attempts_count":2,"last_attempt":{"Time":"2023-04-19T19:49:06+03:00","Valid":true}}]},{"login":"chopchik","contest_result":0,"penalty":0,"problems_result":[{"result":0,"attempts_count":0,"last_attempt":{"Time":"2023-05-08T02:10:26+03:00","Valid":true}}]},{"login":"admin","contest_result":0,"penalty":0,"problems_result":[{"result":0,"attempts_count":0,"last_attempt":{"Time":"2023-05-08T02:18:54+03:00","Valid":true}},{"result":0,"attempts_count":0,"last_attempt":{"Time":"2023-05-07T23:33:07+03:00","Valid":true}},{"result":0,"attempts_count":0,"last_attempt":{"Time":"2023-05-08T17:34:32+03:00","Valid":true}},{"result":0,"attempts_count":0,"last_attempt":{"Time":"2023-05-12T14:56:16+03:00","Valid":true}},{"result":0,"attempts_count":0,"last_attempt":{"Time":"2023-05-12T20:07:57+03:00","Valid":true}},{"result":0,"attempts_count":0,"last_attempt":{"Time":"2023-05-12T20:24:20+03:00","Valid":true}}]}]}

  return (
    <div className={styles.MainPage}>
      <div className={styles.Content}>
        <div className={styles.Header}>
          <span>Результаты:</span>
          <input placeholder="Поиск" className={styles.SearchInput} />
        </div>
        <table className={`${styles.tableSettings} ${tableStyles.worldResTable} ${tableStyles.tasks}`}>
            <tr>
              <th>№</th>
              <th>Имя пользователя</th>
              <th>Счет</th>
              <th>Штраф</th>
              {showCounters()}
            </tr>
            {showStandings()}
        </table>
      </div>
    </div>
  );
};

export default Standings;
