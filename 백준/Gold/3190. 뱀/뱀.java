import java.io.*;
import java.util.*;

class snake {
    int x;
    int y;

    snake(int x, int y) {
        this.x = x;
        this.y = y;
    }

}


public class Main {
    static int N, K;
    static int[][] map;
    static Queue<snake> queue = new LinkedList<>();
    static Deque<snake> dpQ = new LinkedList<>();


    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        StringBuilder sb = new StringBuilder();

        N = Integer.parseInt(st.nextToken());


        K = Integer.parseInt(br.readLine());
        map = new int[N][N];
        // 뱀 크기 , 위치
        queue.add(new snake(0, 0));
        int hx = 0;
        int hy = 0;
        map[hx][hy] = 1;
        // 방향 큐 설정
        dpQ.add(new snake(0, 1));
        dpQ.add(new snake(1, 0));
        dpQ.add(new snake(0, -1));
        dpQ.add(new snake(-1, 0));


        //사과 위치
        for (int i = 0; i < K; i++) {
            st = new StringTokenizer(br.readLine());
            int x = Integer.parseInt(st.nextToken());
            int y = Integer.parseInt(st.nextToken());
            map[x - 1][y - 1] = 3;
        }
        int L = Integer.parseInt(br.readLine());
        int count = 0;
        st = new StringTokenizer(br.readLine());
        int x = Integer.parseInt(st.nextToken());
        String str = st.nextToken();

        for (int j = 0; ; j++) {
            if (x == j) {
                switch (str) {
                    case "D":
                        dpQ.add(dpQ.poll());
                        break;
                    case "L":

                        dpQ.addFirst(dpQ.pollLast());
                        break;
                }
                L--;

                if (L > 0) {
                    st = new StringTokenizer(br.readLine());
                    x = Integer.parseInt(st.nextToken());
                    str = st.nextToken();


                }

            }

            hx += dpQ.peek().x;
            hy += dpQ.peek().y;
            count++;
            if (hx >= N || hy >= N || hx < 0 || hy < 0) {
                break;
            } else if (map[hx][hy] == 3) {
                queue.add(new snake(hx, hy));
                map[hx][hy] = 1;
            } else if (map[hx][hy] == 1) {
                break;
            } else {
                queue.add(new snake(hx, hy));
                map[hx][hy] = 1;
                map[queue.peek().x][queue.peek().y] = 0;
                queue.remove();

            }


        }

        System.out.println(count);


    }
}
