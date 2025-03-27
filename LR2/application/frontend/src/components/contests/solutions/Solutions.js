import React, { useEffect, useState } from "react";
import styles from '../TaskResultStyles.module.css';
import { useParams } from "react-router-dom";
import { MakeAuthorizedRequest, MakeRequest } from "../../../API/RequestService";
import TokenController from "../../../controllers/TokenController";

const Submissions = () =>{
    const [submissions, setSubmissions] = useState();
    const {problemId} = useParams();

    useEffect(() => {
        async function handleSubmissions() {
            const requestOptions = {
                method: 'GET',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': TokenController.getToken()
                },
                credentials: 'include'
              };
          let response = await MakeAuthorizedRequest(`submissions/${problemId}`, requestOptions)
          
          setSubmissions(response.data.submissions)
        }
        handleSubmissions();
      }, [problemId]);

    function makeSubmissionInfo(submission) {
        return <tr>
            <td>{submission.id}</td>
            <td>{submission.submit_time.toLocaleString() + ""}</td>
            <td>{TokenController.getUserNickname()}</td>
            <td>{submission.verdict.time + " ms"}</td>
            <td>{submission.verdict.memory / 1024 + " KB"}</td>
            <td>GNU C++20</td>
            <td>{submission.verdict.status}</td>
        </tr>
    }

    function showSubmissions() {
        if (!submissions) {
            return <></>
        }
        const elements = []
        submissions.map((submission => {
            elements.push(makeSubmissionInfo(submission))
        }))
        return elements
    }

    return (
        <div  className={styles.MainPage}>
            <div className={styles.Content}>
                <span className={styles.Header}>
                    Мои решения:
                </span>
                <table className={styles.tableSettings}>
                    <tr>
                        <td>№ Решения</td>
                        <td>Дата</td>
                        <td>Имя пользователя</td>
                        <td>Время</td>
                        <td>Память</td>
                        <td>Компилятор</td>
                        <td>Вердикт</td>
                    </tr>
                    {showSubmissions()}
                </table>
            </div>
        </div>
    )
}

export default Submissions